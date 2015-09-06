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

from thinc.api cimport Example, ExampleC


from ..structs cimport TokenC

from ..tokens.doc cimport Doc
from ..strings cimport StringStore


from .transition_system import OracleError
from .transition_system cimport TransitionSystem, Transition

from ..gold cimport GoldParse

from . import _parse_features
from ._parse_features cimport CONTEXT_SIZE
from ._parse_features cimport fill_context
from .stateclass cimport StateClass

from .._ml cimport arg_max_if_true


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
    elif name.startswith('embed'):
        return (pf.words, pf.tags, pf.labels)
    else:
        return (pf.unigrams + pf.s0_n0 + pf.s1_n0 + pf.s1_s0 + pf.s0_n1 + pf.n0_n1 + \
                pf.tree_shape + pf.trigrams)


def ParserFactory(transition_system):
    return lambda strings, dir_: Parser(strings, dir_, transition_system)


cdef class Parser:
    def __init__(self, StringStore strings, transition_system, model):
        self.moves = transition_system
        self.model = model

    @classmethod
    def from_dir(cls, model_dir, strings, transition_system):
        if not os.path.exists(model_dir):
            print >> sys.stderr, "Warning: No model found at", model_dir
        elif not os.path.isdir(model_dir):
            print >> sys.stderr, "Warning: model path:", model_dir, "is not a directory"
        cfg = Config.read(model_dir, 'config')
        moves = transition_system(strings, cfg.labels)
        templates = get_templates(cfg.features)
        model = Model(moves.n_moves, templates, model_dir)
        return cls(strings, moves, model)


    def __call__(self, Doc tokens):
        cdef StateClass stcls = StateClass.init(tokens.data, tokens.length)
        self.moves.initialize_state(stcls)

        cdef Example eg = Example(self.model.n_classes, CONTEXT_SIZE,
                                  self.model.n_feats, self.model.n_feats)
        self.parse(stcls, eg.c)
        tokens.set_parse(stcls._sent)

    cdef void predict(self, StateClass stcls, ExampleC* eg) nogil:
        memset(eg.scores, 0, eg.nr_class * sizeof(weight_t))
        self.moves.set_valid(eg.is_valid, stcls)
        fill_context(eg.atoms, stcls)
        self.model.set_scores(eg.scores, eg.atoms)
        eg.guess = arg_max_if_true(eg.scores, eg.is_valid, self.model.n_classes)

    cdef void parse(self, StateClass stcls, ExampleC eg) nogil:
        while not stcls.is_final():
            self.predict(stcls, &eg)
            if not eg.is_valid[eg.guess]:
                break
            self.moves.c[eg.guess].do(stcls, self.moves.c[eg.guess].label)
        self.moves.finalize_state(stcls)

    def train(self, Doc tokens, GoldParse gold):
        self.moves.preprocess_gold(gold)
        cdef StateClass stcls = StateClass.init(tokens.data, tokens.length)
        self.moves.initialize_state(stcls)
        cdef Example eg = Example(self.model.n_classes, CONTEXT_SIZE,
                                  self.model.n_feats, self.model.n_feats)
        cdef weight_t loss = 0
        words = [w.orth_ for w in tokens]
        cdef Transition G
        while not stcls.is_final():
            memset(eg.c.scores, 0, eg.c.nr_class * sizeof(weight_t))
            self.moves.set_costs(eg.c.is_valid, eg.c.costs, stcls, gold)
            fill_context(eg.c.atoms, stcls)
            self.model.train(eg)
            G = self.moves.c[eg.c.guess]

            self.moves.c[eg.c.guess].do(stcls, self.moves.c[eg.c.guess].label)
            loss += eg.c.loss
        return loss

    def step_through(self, Doc doc):
        return StepwiseState(self, doc)


cdef class StepwiseState:
    cdef readonly StateClass stcls
    cdef readonly Example eg
    cdef readonly Doc doc
    cdef readonly Parser parser

    def __init__(self, Parser parser, Doc doc):
        self.parser = parser
        self.doc = doc
        self.stcls = StateClass.init(doc.data, doc.length)
        self.parser.moves.initialize_state(self.stcls)
        self.eg = Example(self.parser.model.n_classes, CONTEXT_SIZE,
                          self.parser.model.n_feats, self.parser.model.n_feats)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.finish()

    @property
    def is_final(self):
        return self.stcls.is_final()

    @property
    def stack(self):
        return self.stcls.stack

    @property
    def queue(self):
        return self.stcls.queue

    @property
    def heads(self):
        return [self.stcls.H(i) for i in range(self.stcls.length)]

    @property
    def deps(self):
        return [self.doc.vocab.strings[self.stcls._sent[i].dep]
                for i in range(self.stcls.length)]

    def predict(self):
        self.parser.predict(self.stcls, &self.eg.c)
        action = self.parser.moves.c[self.eg.c.guess]
        return self.parser.moves.move_name(action.move, action.label)

    def transition(self, action_name):
        moves = {'S': 0, 'D': 1, 'L': 2, 'R': 3}
        if action_name == '_':
            action_name = self.predict()
            action = self.parser.moves.lookup_transition(action_name)
        elif action_name == 'L' or action_name == 'R':
            self.predict()
            move = moves[action_name]
            clas = _arg_max_clas(self.eg.c.scores, move, self.parser.moves.c,
                                 self.eg.c.nr_class)
            action = self.parser.moves.c[clas]
        else:
            action = self.parser.moves.lookup_transition(action_name)
        action.do(self.stcls, action.label)

    def finish(self):
        if self.stcls.is_final():
            self.parser.moves.finalize_state(self.stcls)
        self.doc.set_parse(self.stcls._sent)


cdef int _arg_max_clas(const weight_t* scores, int move, const Transition* actions,
                       int nr_class) except -1:
    cdef weight_t score = 0
    cdef int mode = -1
    cdef int i
    for i in range(nr_class):
        if actions[i].move == move and (mode == -1 or scores[i] >= score):
            mode = i
            score = scores[i]
    return mode
