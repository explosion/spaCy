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
        cdef StateClass stcls = StateClass.init(tokens.data, tokens.length)
        self.moves.initialize_state(stcls)

        cdef Example eg = Example(self.model.n_classes, CONTEXT_SIZE,
                                  self.model.n_feats, self.model.n_feats)
        with nogil:
            self.parse(stcls, eg.c)
        tokens.set_parse(stcls._sent)

    cdef void parse(self, StateClass stcls, ExampleC eg) nogil:
        while not stcls.is_final():
            memset(eg.scores, 0, eg.nr_class * sizeof(weight_t))
            self.moves.set_valid(eg.is_valid, stcls)
            fill_context(eg.atoms, stcls)
            self.model.set_scores(eg.scores, eg.atoms)
            eg.guess = arg_max_if_true(eg.scores, eg.is_valid, self.model.n_classes)
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
