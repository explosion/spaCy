# cython: profile=True
"""
MALT-style dependency parser
"""
from __future__ import unicode_literals
cimport cython
from libc.stdint cimport uint32_t, uint64_t
from libc.string cimport memset, memcpy
import random
import os.path
from os import path
import shutil
import json

from cymem.cymem cimport Pool, Address
from murmurhash.mrmr cimport hash64
from thinc.typedefs cimport weight_t, class_t, feat_t, atom_t


from util import Config

from thinc.features cimport Extractor
from thinc.features cimport Feature
from thinc.features cimport count_feats

from thinc.learner cimport LinearModel

from thinc.search cimport Beam
from thinc.search cimport MaxViolation

from ..tokens cimport Tokens, TokenC
from ..strings cimport StringStore

from .arc_eager cimport TransitionSystem, Transition
from .transition_system import OracleError

from ._state cimport State, new_state, copy_state, is_final, push_stack
from ..gold cimport GoldParse

from . import _parse_features
from ._parse_features cimport fill_context, CONTEXT_SIZE


DEBUG = False
def set_debug(val):
    global DEBUG
    DEBUG = val


cdef unicode print_state(State* s, list words):
    words = list(words) + ['EOL']
    top = words[s.stack[0]] + '_%d' % s.sent[s.stack[0]].head
    second = words[s.stack[-1]] + '_%d' % s.sent[s.stack[-1]].head
    third = words[s.stack[-2]] + '_%d' % s.sent[s.stack[-2]].head
    n0 = words[s.i] if s.i < len(words) else 'EOL'
    n1 = words[s.i + 1] if s.i+1 < len(words) else 'EOL'
    if s.ents_len:
        ent = '%s %d-%d' % (s.ent.label, s.ent.start, s.ent.end)
    else:
        ent = '-'
    return ' '.join((ent, str(s.stack_len), third, second, top, '|', n0, n1))


def get_templates(name):
    pf = _parse_features
    if name == 'ner':
        return pf.ner
    elif name == 'debug':
        return pf.unigrams
    else:
        return (pf.unigrams + pf.s0_n0 + pf.s1_n0 + pf.s0_n1 + pf.n0_n1 + \
                pf.tree_shape + pf.trigrams)


cdef class Parser:
    def __init__(self, StringStore strings, model_dir, transition_system):
        assert os.path.exists(model_dir) and os.path.isdir(model_dir)
        self.cfg = Config.read(model_dir, 'config')
        self.moves = transition_system(strings, self.cfg.labels)
        templates = get_templates(self.cfg.features)
        self.model = Model(self.moves.n_moves, templates, model_dir)

    def __call__(self, Tokens tokens):
        if tokens.length == 0:
            return 0
        if self.cfg.beam_width == 1:
            self._greedy_parse(tokens)
        else:
            self._beam_parse(tokens)

    def train(self, Tokens tokens, GoldParse gold):
        self.moves.preprocess_gold(gold)
        if self.cfg.beam_width == 1:
            return self._greedy_train(tokens, gold)
        else:
            return self._beam_train(tokens, gold)

    cdef int _greedy_parse(self, Tokens tokens) except -1:
        cdef atom_t[CONTEXT_SIZE] context
        cdef int n_feats
        cdef Pool mem = Pool()
        cdef State* state = new_state(mem, tokens.data, tokens.length)
        self.moves.initialize_state(state)
        cdef Transition guess
        while not is_final(state):
            fill_context(context, state)
            scores = self.model.score(context)
            guess = self.moves.best_valid(scores, state)
            guess.do(&guess, state)
        self.moves.finalize_state(state)
        tokens.set_parse(state.sent)

    cdef int _beam_parse(self, Tokens tokens) except -1:
        cdef Beam beam = Beam(self.moves.n_moves, self.cfg.beam_width)
        beam.initialize(_init_state, tokens.length, tokens.data)
        while not beam.is_done:
            self._advance_beam(beam, None, False)
        state = <State*>beam.at(0)
        self.moves.finalize_state(state)
        tokens.set_parse(state.sent)

    def _greedy_train(self, Tokens tokens, GoldParse gold):
        cdef Pool mem = Pool()
        cdef State* state = new_state(mem, tokens.data, tokens.length)
        self.moves.initialize_state(state)

        cdef int cost
        cdef const Feature* feats
        cdef const weight_t* scores
        cdef Transition guess
        cdef Transition best
        cdef atom_t[CONTEXT_SIZE] context
        loss = 0
        while not is_final(state):
            fill_context(context, state)
            scores = self.model.score(context)
            guess = self.moves.best_valid(scores, state)
            best = self.moves.best_gold(scores, state, gold)
            cost = guess.get_cost(&guess, state, &gold.c)
            self.model.update(context, guess.clas, best.clas, cost)
            guess.do(&guess, state)
            loss += cost
        return loss

    def _beam_train(self, Tokens tokens, GoldParse gold_parse):
        cdef Beam pred = Beam(self.moves.n_moves, self.cfg.beam_width)
        pred.initialize(_init_state, tokens.length, tokens.data)
        cdef Beam gold = Beam(self.moves.n_moves, self.cfg.beam_width)
        gold.initialize(_init_state, tokens.length, tokens.data)

        violn = MaxViolation()
        while not pred.is_done and not gold.is_done:
            self._advance_beam(pred, gold_parse, False)
            self._advance_beam(gold, gold_parse, True)
            violn.check(pred, gold)
        if pred.loss >= 1:
            counts = {clas: {} for clas in range(self.model.n_classes)}
            self._count_feats(counts, tokens, violn.g_hist, 1)
            self._count_feats(counts, tokens, violn.p_hist, -1)
        else:
            counts = {}
        self.model._model.update(counts)
        return pred.loss

    def _advance_beam(self, Beam beam, GoldParse gold, bint follow_gold):
        cdef atom_t[CONTEXT_SIZE] context
        cdef State* state
        cdef int i, j, cost
        cdef bint is_valid
        cdef const Transition* move
        for i in range(beam.size):
            state = <State*>beam.at(i)
            fill_context(context, state)
            self.model.set_scores(beam.scores[i], context)
            self.moves.set_valid(beam.is_valid[i], state)
       
        if gold is not None:
            for i in range(beam.size):
                state = <State*>beam.at(i)
                self.moves.set_costs(beam.costs[i], state, gold)
                if follow_gold:
                    for j in range(self.moves.n_moves):
                        beam.is_valid[i][j] = beam.costs[i][j] == 0
        beam.advance(_transition_state, <void*>self.moves.c)
        state = <State*>beam.at(0)
        if state.sent[state.i].sent_end:
            beam.size = int(beam.size / 2)
        beam.check_done(_check_final_state, NULL)

    def _count_feats(self, dict counts, Tokens tokens, list hist, int inc):
        cdef atom_t[CONTEXT_SIZE] context
        cdef Pool mem = Pool()
        cdef State* state = new_state(mem, tokens.data, tokens.length)
        self.moves.initialize_state(state)

        cdef class_t clas
        cdef int n_feats
        for clas in hist:
            if is_final(state):
                break
            fill_context(context, state)
            feats = self.model._extractor.get_feats(context, &n_feats)
            count_feats(counts[clas], feats, n_feats, inc)
            self.moves.c[clas].do(&self.moves.c[clas], state)


# These are passed as callbacks to thinc.search.Beam

cdef int _transition_state(void* _dest, void* _src, class_t clas, void* _moves) except -1:
    dest = <State*>_dest
    src = <const State*>_src
    moves = <const Transition*>_moves
    copy_state(dest, src)
    moves[clas].do(&moves[clas], dest)


cdef void* _init_state(Pool mem, int length, void* tokens) except NULL:
    state = new_state(mem, <const TokenC*>tokens, length)
    push_stack(state)
    return state


cdef int _check_final_state(void* state, void* extra_args) except -1:
    return is_final(<State*>state)
