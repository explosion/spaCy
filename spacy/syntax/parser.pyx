"""
MALT-style dependency parser
"""
from __future__ import unicode_literals
cimport cython
from libc.stdint cimport uint32_t, uint64_t
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

from ..tokens cimport Tokens, TokenC
from ..strings cimport StringStore

from .arc_eager cimport TransitionSystem, Transition
from .transition_system import OracleError

from ._state cimport new_state, State, is_final, get_idx, get_s0, get_s1, get_n0, get_n1
from .conll cimport GoldParse

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
    n0 = words[s.i]
    n1 = words[s.i + 1]
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


cdef class GreedyParser:
    def __init__(self, StringStore strings, model_dir, transition_system):
        assert os.path.exists(model_dir) and os.path.isdir(model_dir)
        self.cfg = Config.read(model_dir, 'config')
        self.moves = transition_system(strings, self.cfg.labels)
        templates = get_templates(self.cfg.features)
        self.model = Model(self.moves.n_moves, templates, model_dir)

    def __call__(self, Tokens tokens):
        if tokens.length == 0:
            return 0

        cdef atom_t[CONTEXT_SIZE] context
        cdef int n_feats
        cdef Pool mem = Pool()
        cdef State* state = new_state(mem, tokens.data, tokens.length)
        self.moves.first_state(state)
        cdef Transition guess
        while not is_final(state):
            fill_context(context, state)
            scores = self.model.score(context)
            guess = self.moves.best_valid(scores, state)
            guess.do(&guess, state)
        tokens.set_parse(state.sent)
        return 0

    def train(self, Tokens tokens, GoldParse gold):
        self.moves.preprocess_gold(gold)
        cdef Pool mem = Pool()
        cdef State* state = new_state(mem, tokens.data, tokens.length)
        self.moves.first_state(state)

        cdef int cost
        cdef const Feature* feats
        cdef const weight_t* scores
        cdef Transition guess
        cdef Transition best
        cdef atom_t[CONTEXT_SIZE] context

        while not is_final(state):
            fill_context(context, state)
            scores = self.model.score(context)

            guess = self.moves.best_valid(scores, state)
            best = self.moves.best_gold(scores, state, gold)
            
            cost = guess.get_cost(&guess, state, gold)
            self.model.update(context, guess.clas, best.clas, cost)

            guess.do(&guess, state)
