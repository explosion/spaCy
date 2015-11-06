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
from thinc.features cimport ConjunctionExtracter

from util import Config

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


cdef class ParserModel(AveragedPerceptron):
    def __init__(self, n_classes, templates):
        AveragedPerceptron.__init__(self, n_classes,
            ConjunctionExtracter(CONTEXT_SIZE, templates))

    cdef void set_features(self, ExampleC* eg, StateClass stcls) except *: 
        fill_context(eg.atoms, stcls)
        eg.nr_feat = self.extracter.set_features(eg.features, eg.atoms)


cdef class Parser:
    def __init__(self, StringStore strings, transition_system, ParserModel model):
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
        model = ParserModel(moves.n_moves, templates)
        if path.exists(path.join(model_dir, 'model')):
            model.load(path.join(model_dir, 'model'))
        return cls(strings, moves, model)

    def __reduce__(self):
        return (Parser, (self.moves.strings, self.moves, self.model), None, None)

    def __call__(self, Doc tokens):
        cdef StateClass stcls = StateClass.init(tokens.c, tokens.length)
        self.moves.initialize_state(stcls)

        cdef Pool mem = Pool()
        cdef ExampleC eg = self.model.allocate(mem)
        while not stcls.is_final():
            self.model.set_features(&eg, stcls)
            self.moves.set_valid(eg.is_valid, stcls)
            self.model.set_prediction(&eg)

            action = self.moves.c[eg.guess]
            if not eg.is_valid[eg.guess]:
                raise ValueError(
                    "Illegal action: %s" % self.moves.move_name(action.move, action.label)
                )
            
            action.do(stcls, action.label)
        self.moves.finalize_state(stcls)
        tokens.set_parse(stcls._sent)
  
    def train(self, Doc tokens, GoldParse gold):
        self.moves.preprocess_gold(gold)
        cdef StateClass stcls = StateClass.init(tokens.c, tokens.length)
        self.moves.initialize_state(stcls)
        cdef Pool mem = Pool()
        cdef ExampleC eg = self.model.allocate(mem)
        cdef weight_t loss = 0
        words = [w.orth_ for w in tokens]
        cdef Transition action
        while not stcls.is_final():
            self.model.set_features(&eg, stcls)
            self.moves.set_costs(eg.is_valid, eg.costs, stcls, gold)
            self.model.set_prediction(&eg)
            self.model.update(&eg)

            action = self.moves.c[eg.guess]
            action.do(stcls, action.label)
            loss += eg.costs[eg.guess]
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
        self.stcls = StateClass.init(doc.c, doc.length)
        self.parser.moves.initialize_state(self.stcls)
        self.eg = Example(self.parser.model.nr_class, CONTEXT_SIZE,
                          self.parser.model.nr_feat, self.parser.model.nr_embed)

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
        self.parser.model.set_features(&self.eg.c, self.stcls)
        self.parser.moves.set_valid(self.eg.c.is_valid, self.stcls)
        self.parser.model.set_prediction(&self.eg.c)

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
