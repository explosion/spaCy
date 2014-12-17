# cython: profile=True
"""
MALT-style dependency parser
"""
from __future__ import unicode_literals
cimport cython
import random
import os.path
from os.path import join as pjoin
import shutil
import json

from cymem.cymem cimport Pool, Address
from thinc.typedefs cimport weight_t, class_t, feat_t, atom_t


from util import Config

from thinc.features cimport Extractor
from thinc.features cimport Feature
from thinc.features cimport count_feats

from thinc.learner cimport LinearModel

from ..tokens cimport Tokens, TokenC

from .arc_eager cimport TransitionSystem

from ._state cimport init_state, State, is_final, get_idx, get_s0, get_s1

from . import _parse_features
from ._parse_features cimport fill_context, CONTEXT_SIZE


DEBUG = False 
def set_debug(val):
    global DEBUG
    DEBUG = val


cdef unicode print_state(State* s, list words):
    words = list(words) + ['EOL']
    top = words[s.stack[0]]
    second = words[s.stack[-1]]
    n0 = words[s.i]
    n1 = words[s.i + 1]
    return ' '.join((second, top, '|', n0, n1))


def get_templates(name):
    pf = _parse_features
    if name == 'zhang':
        return pf.arc_eager
    else:
        templs = pf.unigrams + pf.s0_n0 + pf.s1_n0 + pf.s0_n1 + pf.n0_n1 + pf.tree_shape + pf.trigrams
        return templs


cdef class GreedyParser:
    def __init__(self, model_dir):
        assert os.path.exists(model_dir) and os.path.isdir(model_dir)
        self.cfg = Config.read(model_dir, 'config')
        self.extractor = Extractor(get_templates(self.cfg.features))
        self.moves = TransitionSystem(self.cfg.left_labels, self.cfg.right_labels)
        self.model = LinearModel(self.moves.n_moves, self.extractor.n_templ)
        if os.path.exists(pjoin(model_dir, 'model')):
            self.model.load(pjoin(model_dir, 'model'))

    cpdef int parse(self, Tokens tokens) except -1:
        cdef:
            Feature* feats
            const weight_t* scores
            int guess

        cdef atom_t[CONTEXT_SIZE] context
        cdef int n_feats
        cdef Pool mem = Pool()
        cdef State* state = init_state(mem, tokens.data, tokens.length)
        while not is_final(state):
            fill_context(context, state)
            feats = self.extractor.get_feats(context, &n_feats)
            scores = self.model.get_scores(feats, n_feats)
            guess = self.moves.best_valid(scores, state)
            self.moves.transition(state, guess)
        return 0

    def train_sent(self, Tokens tokens, list gold_heads, list gold_labels):
        cdef:
            Feature* feats
            weight_t* scores

        cdef int n_feats
        cdef atom_t[CONTEXT_SIZE] context
        cdef Pool mem = Pool()
        cdef int* heads_array = <int*>mem.alloc(tokens.length, sizeof(int))
        cdef int* labels_array = <int*>mem.alloc(tokens.length, sizeof(int))
        cdef int i
        for i in range(tokens.length):
            heads_array[i] = gold_heads[i]
            labels_array[i] = self.moves.label_ids[gold_labels[i]]
        
        cdef State* state = init_state(mem, tokens.data, tokens.length)
        while not is_final(state):
            fill_context(context, state) 
            feats = self.extractor.get_feats(context, &n_feats)
            scores = self.model.get_scores(feats, n_feats)
            guess = self.moves.best_valid(scores, state)
            best = self.moves.best_gold(scores, state, heads_array, labels_array)
            counts = _get_counts(guess, best, feats, n_feats)
            self.model.update(counts)
            self.moves.transition(state, guess)
        cdef int n_corr = 0
        for i in range(tokens.length):
            n_corr += (i + state.sent[i].head) == gold_heads[i]
        return n_corr


cdef dict _get_counts(int guess, int best, const Feature* feats, const int n_feats):
    if guess == best:
        return {}

    gold_counts = {}
    guess_counts = {}
    cdef int i
    for i in range(n_feats):
        key = (feats[i].i, feats[i].key)
        if key in gold_counts:
            gold_counts[key] += feats[i].value
            guess_counts[key] -= feats[i].value
        else:
            gold_counts[key] = feats[i].value
            guess_counts[key] = -feats[i].value
    return {guess: guess_counts, best: gold_counts}

