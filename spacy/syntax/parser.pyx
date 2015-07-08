# cython: profile=True
"""
MALT-style dependency parser
"""
from __future__ import unicode_literals
cimport cython

from cpython.ref cimport PyObject, Py_INCREF, Py_XDECREF

from libc.stdint cimport uint32_t, uint64_t
from libc.string cimport memset, memcpy
import random
import os.path
from os import path
import shutil
import json
import sys

from cymem.cymem cimport Pool, Address
from murmurhash.mrmr cimport hash64
from thinc.typedefs cimport weight_t, class_t, feat_t, atom_t, hash_t


from util import Config

from thinc.features cimport Extractor
from thinc.features cimport Feature
from thinc.features cimport count_feats

from thinc.learner cimport LinearModel

from thinc.search cimport Beam
from thinc.search cimport MaxViolation

from ..tokens cimport Doc, TokenC
from ..strings cimport StringStore


from .transition_system import OracleError
from .transition_system cimport TransitionSystem, Transition

from ..gold cimport GoldParse

from . import _parse_features
from ._parse_features cimport CONTEXT_SIZE
from ._parse_features cimport fill_context
from .stateclass cimport StateClass


DEBUG = False
def set_debug(val):
    global DEBUG
    DEBUG = val


def get_templates(name):
    pf = _parse_features
    if name == 'ner':
        return pf.ner
    elif name == 'debug':
        return pf.unigrams
    else:
        return (pf.unigrams + pf.s0_n0 + pf.s1_n0 + pf.s1_s0 + pf.s0_n1 + pf.n0_n1 + \
                pf.tree_shape + pf.trigrams)


def ParserFactory(transition_system):
    return lambda strings, dir_: Parser(strings, dir_, transition_system)


cdef class Parser:
    def __init__(self, StringStore strings, model_dir, transition_system):
        if not os.path.exists(model_dir):
            print >> sys.stderr, "Warning: No model found at", model_dir
        elif not os.path.isdir(model_dir):
            print >> sys.stderr, "Warning: model path:", model_dir, "is not a directory"
        else:
            self.cfg = Config.read(model_dir, 'config')
            self.moves = transition_system(strings, self.cfg.labels)
            templates = get_templates(self.cfg.features)
            self.model = Model(self.moves.n_moves, templates, model_dir)

    def __call__(self, Doc tokens):
        if self.model is not None:
            if self.cfg.get('beam_width', 0) < 1:
                self._greedy_parse(tokens)
            else:
                self._beam_parse(tokens)

    def train(self, Doc tokens, GoldParse gold):
        self.moves.preprocess_gold(gold)
        if self.cfg.get('beam_width', 0) < 1:
            return self._greedy_train(tokens, gold)
        else:
            return self._beam_train(tokens, gold)

    cdef int _greedy_parse(self, Doc tokens) except -1:
        cdef atom_t[CONTEXT_SIZE] context
        cdef int n_feats
        cdef Pool mem = Pool()
        cdef StateClass stcls = StateClass.init(tokens.data, tokens.length)
        self.moves.initialize_state(stcls)
        cdef Transition guess
        words = [w.orth_ for w in tokens]
        while not stcls.is_final():
            fill_context(context, stcls)
            scores = self.model.score(context)
            guess = self.moves.best_valid(scores, stcls)
            #print self.moves.move_name(guess.move, guess.label), stcls.print_state(words)
            guess.do(stcls, guess.label)
            assert stcls._s_i >= 0
        self.moves.finalize_state(stcls)
        tokens.set_parse(stcls._sent)

    cdef int _beam_parse(self, Doc tokens) except -1:
        cdef Beam beam = Beam(self.moves.n_moves, self.cfg.beam_width)
        words = [w.orth_ for w in tokens]
        beam.initialize(_init_state, tokens.length, tokens.data)
        beam.check_done(_check_final_state, NULL)
        while not beam.is_done:
            self._advance_beam(beam, None, False, words)
        state = <StateClass>beam.at(0)
        self.moves.finalize_state(state)
        tokens.set_parse(state._sent)
        _cleanup(beam)

    def _greedy_train(self, Doc tokens, GoldParse gold):
        cdef Pool mem = Pool()
        cdef StateClass stcls = StateClass.init(tokens.data, tokens.length)
        self.moves.initialize_state(stcls)

        cdef int cost
        cdef const Feature* feats
        cdef const weight_t* scores
        cdef Transition guess
        cdef Transition best
        cdef atom_t[CONTEXT_SIZE] context
        loss = 0
        words = [w.orth_ for w in tokens]
        history = []
        while not stcls.is_final():
            fill_context(context, stcls)
            scores = self.model.score(context)
            guess = self.moves.best_valid(scores, stcls)
            best = self.moves.best_gold(scores, stcls, gold)
            cost = guess.get_cost(stcls, &gold.c, guess.label)
            self.model.update(context, guess.clas, best.clas, cost)
            guess.do(stcls, guess.label)
            loss += cost
        return loss

    def _beam_train(self, Doc tokens, GoldParse gold_parse):
        cdef Beam pred = Beam(self.moves.n_moves, self.cfg.beam_width)
        pred.initialize(_init_state, tokens.length, tokens.data)
        pred.check_done(_check_final_state, NULL)
        cdef Beam gold = Beam(self.moves.n_moves, self.cfg.beam_width)
        gold.initialize(_init_state, tokens.length, tokens.data)
        gold.check_done(_check_final_state, NULL)

        violn = MaxViolation()
        words = [w.orth_ for w in tokens]
        while not pred.is_done and not gold.is_done:
            self._advance_beam(pred, gold_parse, False, words)
            self._advance_beam(gold, gold_parse, True, words)
            violn.check(pred, gold)
        if pred.loss >= 1:
            counts = {clas: {} for clas in range(self.model.n_classes)}
            self._count_feats(counts, tokens, violn.g_hist, 1)
            self._count_feats(counts, tokens, violn.p_hist, -1)
        else:
            counts = {}
        self.model._model.update(counts)
        _cleanup(pred)
        _cleanup(gold)
        return pred.loss

    def _advance_beam(self, Beam beam, GoldParse gold, bint follow_gold, words):
        cdef atom_t[CONTEXT_SIZE] context
        cdef int i, j, cost
        cdef bint is_valid
        cdef const Transition* move
        for i in range(beam.size):
            stcls = <StateClass>beam.at(i)
            if not stcls.is_final():
                fill_context(context, stcls)
                self.model.set_scores(beam.scores[i], context)
                self.moves.set_valid(beam.is_valid[i], stcls)
        if gold is not None:
            for i in range(beam.size):
                stcls = <StateClass>beam.at(i)
                if not stcls.is_final():
                    self.moves.set_costs(beam.costs[i], stcls, gold)
                    if follow_gold:
                        for j in range(self.moves.n_moves):
                            beam.is_valid[i][j] *= beam.costs[i][j] == 0
        beam.advance(_transition_state, _hash_state, <void*>self.moves.c)
        beam.check_done(_check_final_state, NULL)

    def _count_feats(self, dict counts, Doc tokens, list hist, int inc):
        cdef atom_t[CONTEXT_SIZE] context
        cdef Pool mem = Pool()
        cdef StateClass stcls = StateClass.init(tokens.data, tokens.length)
        self.moves.initialize_state(stcls)

        cdef class_t clas
        cdef int n_feats
        for clas in hist:
            fill_context(context, stcls)
            feats = self.model._extractor.get_feats(context, &n_feats)
            count_feats(counts[clas], feats, n_feats, inc)
            self.moves.c[clas].do(stcls, self.moves.c[clas].label)


# These are passed as callbacks to thinc.search.Beam

cdef int _transition_state(void* _dest, void* _src, class_t clas, void* _moves) except -1:
    dest = <StateClass>_dest
    src = <StateClass>_src
    moves = <const Transition*>_moves
    dest.clone(src)
    moves[clas].do(dest, moves[clas].label)


cdef void* _init_state(Pool mem, int length, void* tokens) except NULL:
    cdef StateClass st = StateClass.init(<const TokenC*>tokens, length)
    st.fast_forward()
    Py_INCREF(st)
    return <void*>st


cdef int _check_final_state(void* _state, void* extra_args) except -1:
    return (<StateClass>_state).is_final()


def _cleanup(Beam beam):
    for i in range(beam.width):
        Py_XDECREF(<PyObject*>beam._states[i].content)
        Py_XDECREF(<PyObject*>beam._parents[i].content)

cdef hash_t _hash_state(void* _state, void* _) except 0:
    return <hash_t>_state
    
    #state = <const State*>_state
    #cdef atom_t[10] rep

    #rep[0] = state.stack[0] if state.stack_len >= 1 else 0
    #rep[1] = state.stack[-1] if state.stack_len >= 2 else 0
    #rep[2] = state.stack[-2] if state.stack_len >= 3 else 0
    #rep[3] = state.i
    #rep[4] = state.sent[state.stack[0]].l_kids if state.stack_len >= 1 else 0
    #rep[5] = state.sent[state.stack[0]].r_kids if state.stack_len >= 1 else 0
    #rep[6] = state.sent[state.stack[0]].dep if state.stack_len >= 1 else 0
    #rep[7] = state.sent[state.stack[-1]].dep if state.stack_len >= 2 else 0
    #if get_left(state, get_n0(state), 1) != NULL:
    #    rep[8] = get_left(state, get_n0(state), 1).dep 
    #else:
    #    rep[8] = 0
    #rep[9] = state.sent[state.i].l_kids
    #return hash64(rep, sizeof(atom_t) * 10, 0)
