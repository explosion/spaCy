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

from .arc_eager cimport TransitionSystem, Transition

from ._state cimport init_state, State, is_final, get_idx, get_s0, get_s1, get_n0, get_n1

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
    return ' '.join((str(s.stack_len), third, second, top, '|', n0, n1))


def get_templates(name):
    pf = _parse_features
    if name == 'zhang':
        return pf.unigrams, pf.arc_eager
    else:
        return pf.unigrams, (pf.unigrams + pf.s0_n0 + pf.s1_n0 + pf.s0_n1 + pf.n0_n1 + \
                             pf.tree_shape + pf.trigrams)


cdef class GreedyParser:
    def __init__(self, model_dir):
        assert os.path.exists(model_dir) and os.path.isdir(model_dir)
        self.cfg = Config.read(model_dir, 'config')
        self.moves = TransitionSystem(self.cfg.left_labels, self.cfg.right_labels)
        hasty_templ, full_templ = get_templates(self.cfg.features)
        self.model = Model(self.moves.n_moves, full_templ, model_dir)

    def __call__(self, Tokens tokens):
        cdef:
            Transition guess
            uint64_t state_key

        cdef atom_t[CONTEXT_SIZE] context
        cdef int n_feats
        cdef Pool mem = Pool()
        cdef State* state = init_state(mem, tokens.data, tokens.length)
        while not is_final(state):
            fill_context(context, state)
            scores = self.model.score(context)
            guess = self.moves.best_valid(scores, state)
            self.moves.transition(state, &guess)
        # Messily tell Tokens object the string names of the dependency labels
        tokens._dep_strings = [None] * len(self.moves.label_ids)
        for label, id_ in self.moves.label_ids.items():
            tokens._dep_strings[id_] = label
        tokens.is_parsed = True
        return 0

    def train_sent(self, Tokens tokens, list gold_heads, list gold_labels,
                   force_gold=False):
        cdef:
            const Feature* feats
            const weight_t* scores
            Transition guess
            Transition gold

        cdef int n_feats
        cdef atom_t[CONTEXT_SIZE] context
        cdef Pool mem = Pool()
        cdef int* heads_array = <int*>mem.alloc(tokens.length, sizeof(int))
        cdef int* labels_array = <int*>mem.alloc(tokens.length, sizeof(int))
        cdef int i
        for i in range(tokens.length):
            if gold_heads[i] is None:
                heads_array[i] = -1
                labels_array[i] = -1
            else:
                heads_array[i] = gold_heads[i]
                labels_array[i] = self.moves.label_ids[gold_labels[i]]
       
        py_words = [t.orth_ for t in tokens]
        py_moves = ['S', 'D', 'L', 'R', 'BS', 'BR']
        history = []
        #print py_words
        cdef State* state = init_state(mem, tokens.data, tokens.length)
        while not is_final(state):
            fill_context(context, state)
            scores = self.model.score(context)
            guess = self.moves.best_valid(scores, state)
            best = self.moves.best_gold(&guess, scores, state, heads_array, labels_array)
            history.append((py_moves[best.move], print_state(state, py_words)))
            self.model.update(context, guess.clas, best.clas, guess.cost)
            if force_gold:
                self.moves.transition(state, &best)
            else:
                self.moves.transition(state, &guess)
        cdef int n_corr = 0
        for i in range(tokens.length):
            if gold_heads[i] != -1:
            n_corr += (i + state.sent[i].head) == gold_heads[i]
        if force_gold and n_corr != tokens.length:
            print py_words
            print gold_heads
            for move, state_str in history:
                print move, state_str
            for i in range(tokens.length):
                print py_words[i], py_words[i + state.sent[i].head], py_words[gold_heads[i]]
            raise Exception
        return n_corr
