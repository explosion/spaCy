# cython: infer_types=True
"""
MALT-style dependency parser
"""
from __future__ import unicode_literals
cimport cython
cimport cython.parallel

from cpython.ref cimport PyObject, Py_INCREF, Py_XDECREF
from cpython.exc cimport PyErr_CheckSignals

from libc.stdint cimport uint32_t, uint64_t
from libc.string cimport memset, memcpy
from libc.stdlib cimport malloc, calloc, free
import os.path
from os import path
import shutil
import json
import sys
from .nonproj import PseudoProjectivity

from cymem.cymem cimport Pool, Address
from murmurhash.mrmr cimport hash64
from thinc.typedefs cimport weight_t, class_t, feat_t, atom_t, hash_t
from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.linalg cimport VecVec
from thinc.structs cimport SparseArrayC
from preshed.maps cimport MapStruct
from preshed.maps cimport map_get
from thinc.structs cimport FeatureC

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
from ._state cimport StateC


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
    cdef void set_featuresC(self, ExampleC* eg, const StateC* state) nogil: 
        fill_context(eg.atoms, state)
        eg.nr_feat = self.extracter.set_features(eg.features, eg.atoms)


cdef class Parser:
    def __init__(self, StringStore strings, transition_system, ParserModel model, int projectivize = 0):
        self.moves = transition_system
        self.model = model
        self._projectivize = projectivize

    @classmethod
    def from_dir(cls, model_dir, strings, transition_system):
        if not os.path.exists(model_dir):
            print >> sys.stderr, "Warning: No model found at", model_dir
        elif not os.path.isdir(model_dir):
            print >> sys.stderr, "Warning: model path:", model_dir, "is not a directory"
        cfg = Config.read(model_dir, 'config')
        moves = transition_system(strings, cfg.labels)
        templates = get_templates(cfg.features)
        model = ParserModel(templates)
        project = cfg.projectivize if hasattr(cfg,'projectivize') else False
        if path.exists(path.join(model_dir, 'model')):
            model.load(path.join(model_dir, 'model'))
        return cls(strings, moves, model, project)

    @classmethod
    def load(cls, pkg_or_str_or_file, vocab):
        # TODO
        raise NotImplementedError(
                "This should be here, but isn't yet =/. Use Parser.from_dir")

    def __reduce__(self):
        return (Parser, (self.moves.strings, self.moves, self.model), None, None)

    def __call__(self, Doc tokens):
        cdef int nr_class = self.moves.n_moves
        cdef int nr_feat = self.model.nr_feat
        with nogil:
            self.parseC(tokens.c, tokens.length, nr_feat, nr_class)
        # Check for KeyboardInterrupt etc. Untested
        PyErr_CheckSignals()
        self.moves.finalize_doc(tokens)

    def pipe(self, stream, int batch_size=1000, int n_threads=2):
        cdef Pool mem = Pool()
        cdef TokenC** doc_ptr = <TokenC**>mem.alloc(batch_size, sizeof(TokenC*))
        cdef int* lengths = <int*>mem.alloc(batch_size, sizeof(int))
        cdef Doc doc
        cdef int i
        cdef int nr_class = self.moves.n_moves
        cdef int nr_feat = self.model.nr_feat
        cdef int status
        queue = []
        for doc in stream:
            doc_ptr[len(queue)] = doc.c
            lengths[len(queue)] = doc.length
            queue.append(doc)
            if len(queue) == batch_size:
                with nogil:
                    for i in cython.parallel.prange(batch_size, num_threads=n_threads):
                        status = self.parseC(doc_ptr[i], lengths[i], nr_feat, nr_class)
                        if status != 0:
                            with gil:
                                sent_str = queue[i].text
                                raise ValueError("Error parsing doc: %s" % sent_str)
                PyErr_CheckSignals()
                for doc in queue:
                    self.moves.finalize_doc(doc)
                    yield doc
                queue = []
        batch_size = len(queue)
        with nogil:
            for i in cython.parallel.prange(batch_size, num_threads=n_threads):
                status = self.parseC(doc_ptr[i], lengths[i], nr_feat, nr_class)
                if status != 0:
                    with gil:
                        sent_str = queue[i].text
                        raise ValueError("Error parsing doc: %s" % sent_str)
        PyErr_CheckSignals()
        for doc in queue:
            self.moves.finalize_doc(doc)
            yield doc

    cdef int parseC(self, TokenC* tokens, int length, int nr_feat, int nr_class) nogil:
        cdef ExampleC eg
        eg.nr_feat = nr_feat
        eg.nr_atom = CONTEXT_SIZE
        eg.nr_class = nr_class
        eg.features = <FeatureC*>calloc(sizeof(FeatureC), nr_feat)
        eg.atoms = <atom_t*>calloc(sizeof(atom_t), CONTEXT_SIZE)
        eg.scores = <weight_t*>calloc(sizeof(weight_t), nr_class)
        eg.is_valid = <int*>calloc(sizeof(int), nr_class)
        state = new StateC(tokens, length)
        self.moves.initialize_state(state)
        cdef int i
        while not state.is_final():
            self.model.set_featuresC(&eg, state)
            self.moves.set_valid(eg.is_valid, state)
            self.model.set_scoresC(eg.scores, eg.features, eg.nr_feat)

            guess = VecVec.arg_max_if_true(eg.scores, eg.is_valid, eg.nr_class)

            action = self.moves.c[guess]
            if not eg.is_valid[guess]:
                # with gil:
                #     move_name = self.moves.move_name(action.move, action.label)
                #     print 'invalid action:', move_name
                return 1

            action.do(state, action.label)
            memset(eg.scores, 0, sizeof(eg.scores[0]) * eg.nr_class)
            for i in range(eg.nr_class):
                eg.is_valid[i] = 1
        self.moves.finalize_state(state)
        for i in range(length):
            tokens[i] = state._sent[i]
        del state
        free(eg.features)
        free(eg.atoms)
        free(eg.scores)
        free(eg.is_valid)
        return 0
  
    def train(self, Doc tokens, GoldParse gold):
        self.moves.preprocess_gold(gold)
        cdef StateClass stcls = StateClass.init(tokens.c, tokens.length)
        self.moves.initialize_state(stcls.c)
        cdef Pool mem = Pool()
        cdef Example eg = Example(
                nr_class=self.moves.n_moves,
                nr_atom=CONTEXT_SIZE,
                nr_feat=self.model.nr_feat)
        cdef weight_t loss = 0
        cdef Transition action
        while not stcls.is_final():
            self.model.set_featuresC(&eg.c, stcls.c)
            self.moves.set_costs(eg.c.is_valid, eg.c.costs, stcls, gold)
            self.model.set_scoresC(eg.c.scores, eg.c.features, eg.c.nr_feat)
            self.model.updateC(&eg.c)
            guess = VecVec.arg_max_if_true(eg.c.scores, eg.c.is_valid, eg.c.nr_class)

            action = self.moves.c[eg.guess]
            action.do(stcls.c, action.label)
            loss += eg.costs[eg.guess]
            eg.fill_scores(0, eg.nr_class)
            eg.fill_costs(0, eg.nr_class)
            eg.fill_is_valid(0, eg.nr_class)
        return loss

    def step_through(self, Doc doc):
        return StepwiseState(self, doc)

    def from_transition_sequence(self, Doc doc, sequence):
        with self.step_through(doc) as stepwise:
            for transition in sequence:
                stepwise.transition(transition)

    def add_label(self, label):
        for action in self.moves.action_types:
            self.moves.add_action(action, label)


cdef class StepwiseState:
    cdef readonly StateClass stcls
    cdef readonly Example eg
    cdef readonly Doc doc
    cdef readonly Parser parser

    def __init__(self, Parser parser, Doc doc):
        self.parser = parser
        self.doc = doc
        self.stcls = StateClass.init(doc.c, doc.length)
        self.parser.moves.initialize_state(self.stcls.c)
        self.eg = Example(
            nr_class=self.parser.moves.n_moves,
            nr_atom=CONTEXT_SIZE,
            nr_feat=self.parser.model.nr_feat)

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
        return [self.stcls.H(i) for i in range(self.stcls.c.length)]

    @property
    def deps(self):
        return [self.doc.vocab.strings[self.stcls.c._sent[i].dep]
                for i in range(self.stcls.c.length)]

    def predict(self):
        self.eg.reset()
        self.parser.model.set_featuresC(&self.eg.c, self.stcls.c)
        self.parser.moves.set_valid(self.eg.c.is_valid, self.stcls.c)
        self.parser.model.set_scoresC(self.eg.c.scores,
            self.eg.c.features, self.eg.c.nr_feat)

        cdef Transition action = self.parser.moves.c[self.eg.guess]
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
        action.do(self.stcls.c, action.label)

    def finish(self):
        if self.stcls.is_final():
            self.parser.moves.finalize_state(self.stcls.c)
        self.doc.set_parse(self.stcls.c._sent)
        self.parser.moves.finalize_doc(self.doc)


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
