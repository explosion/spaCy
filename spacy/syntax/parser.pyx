# cython: infer_types=True
# cython: profile=True
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
from libc.math cimport exp
import os.path
from os import path
import shutil
import json
import sys
from .nonproj import PseudoProjectivity
import random

from cymem.cymem cimport Pool, Address
from murmurhash.mrmr cimport hash64
from thinc.typedefs cimport weight_t, class_t, feat_t, atom_t, hash_t, idx_t
from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.linalg cimport VecVec
from thinc.structs cimport NeuralNetC, SparseArrayC, ExampleC
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
from ._parse_features cimport *
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
    elif name.startswith('neural'):
        features = pf.words + pf.tags + pf.labels
        slots = [0] * len(pf.words) + [1] * len(pf.tags) + [2] * len(pf.labels)
        return ([(f,) for f in features], slots)
    else:
        return (pf.unigrams + pf.s0_n0 + pf.s1_n0 + pf.s1_s0 + pf.s0_n1 + pf.n0_n1 + \
                pf.tree_shape + pf.trigrams)


def ParserFactory(transition_system):
    return lambda strings, dir_: Parser(strings, dir_, transition_system)


cdef class ParserPerceptron(AveragedPerceptron):
    @property
    def widths(self):
        return (self.extracter.nr_templ,)

    def update(self, Example eg):
        '''Does regression on negative cost. Sort of cute?'''
        self.time += 1
        cdef weight_t loss = 0.0
        best = eg.best
        for clas in range(eg.c.nr_class):
            if not eg.c.is_valid[clas]:
                continue
            if eg.c.scores[clas] < eg.c.scores[best]:
                continue
            loss += (-eg.c.costs[clas] - eg.c.scores[clas]) ** 2
            d_loss = 2 * (-eg.c.costs[clas] - eg.c.scores[clas])
            step = d_loss * 0.001
            for feat in eg.c.features[:eg.c.nr_feat]:
                self.update_weight(feat.key, clas, feat.value * step)
        return int(loss)

    cdef void set_featuresC(self, ExampleC* eg, const void* _state) nogil: 
        state = <const StateC*>_state
        fill_context(eg.atoms, state)
        eg.nr_feat = self.extracter.set_features(eg.features, eg.atoms)


cdef class ParserNeuralNet(NeuralNet):
    def __init__(self, shape, **kwargs):
        vector_widths = [4] * 76
        slots =  [0, 1, 2, 3] # S0
        slots += [4, 5, 6, 7] # S1
        slots += [8, 9, 10, 11] # S2
        slots += [12, 13, 14, 15] # S3+
        slots += [16, 17, 18, 19] # B0
        slots += [20, 21, 22, 23] # B1
        slots += [24, 25, 26, 27] # B2
        slots += [28, 29, 30, 31] # B3+
        slots += [32, 33, 34, 35] * 2 # S0l, S0r
        slots += [36, 37, 38, 39] * 2 # B0l, B0r
        slots += [40, 41, 42, 43] * 2 # S1l, S1r
        slots += [44, 45, 46, 47] * 2 # S2l, S2r
        slots += [48, 49, 50, 51, 52, 53, 54, 55]
        slots += [53, 54, 55, 56]
        input_length = sum(vector_widths[slot] for slot in slots)
        widths = [input_length] + shape
        NeuralNet.__init__(self, widths, embed=(vector_widths, slots), **kwargs)

    @property
    def nr_feat(self):
        return 2000

    cdef void set_featuresC(self, ExampleC* eg, const void* _state) nogil: 
        memset(eg.features, 0, 2000 * sizeof(FeatureC))
        state = <const StateC*>_state
        fill_context(eg.atoms, state)
        feats = eg.features

        feats = _add_token(feats, 0, state.S_(0), 1.0)
        feats = _add_token(feats, 4, state.S_(1), 1.0)
        feats = _add_token(feats, 8, state.S_(2), 1.0)
        # Rest of the stack, with exponential decay
        for i in range(3, state.stack_depth()):
            feats = _add_token(feats, 12, state.S_(i), 1.0 * 0.5**(i-2))
        feats = _add_token(feats, 16, state.B_(0), 1.0)
        feats = _add_token(feats, 20, state.B_(1), 1.0)
        feats = _add_token(feats, 24, state.B_(2), 1.0)
        # Rest of the buffer, with exponential decay
        for i in range(3, min(8, state.buffer_length())):
            feats = _add_token(feats, 28, state.B_(i), 1.0 * 0.5**(i-2))
        feats = _add_subtree(feats, 32, state, state.S(0))
        feats = _add_subtree(feats, 40, state, state.B(0))
        feats = _add_subtree(feats, 48, state, state.S(1))
        feats = _add_subtree(feats, 56, state, state.S(2))
        feats = _add_pos_bigram(feats, 64, state.S_(0), state.B_(0))
        feats = _add_pos_bigram(feats, 65, state.S_(1), state.S_(0))
        feats = _add_pos_bigram(feats, 66, state.S_(1), state.B_(0))
        feats = _add_pos_bigram(feats, 67, state.S_(0), state.B_(1))
        feats = _add_pos_bigram(feats, 68, state.S_(0), state.R_(state.S(0), 1))
        feats = _add_pos_bigram(feats, 69, state.S_(0), state.R_(state.S(0), 2))
        feats = _add_pos_bigram(feats, 70, state.S_(0), state.L_(state.S(0), 1))
        feats = _add_pos_bigram(feats, 71, state.S_(0), state.L_(state.S(0), 2))
        feats = _add_pos_trigram(feats, 72, state.S_(1), state.S_(0), state.B_(0))
        feats = _add_pos_trigram(feats, 73, state.S_(0), state.B_(0), state.B_(1))
        feats = _add_pos_trigram(feats, 74, state.S_(0), state.R_(state.S(0), 1),
                                 state.R_(state.S(0), 2))
        feats = _add_pos_trigram(feats, 75, state.S_(0), state.L_(state.S(0), 1),
                                 state.L_(state.S(0), 2))
        eg.nr_feat = feats - eg.features

    cdef void _set_delta_lossC(self, weight_t* delta_loss,
            const weight_t* Zs, const weight_t* scores) nogil:
        for i in range(self.c.widths[self.c.nr_layer-1]):
            delta_loss[i] = Zs[i]

    cdef void _softmaxC(self, weight_t* out) nogil:
        pass


cdef inline FeatureC* _add_token(FeatureC* feats,
        int slot, const TokenC* token, weight_t value) nogil:
    # Word
    feats.i = slot
    feats.key = token.lex.norm
    feats.value = value
    feats += 1
    # POS tag
    feats.i = slot+1
    feats.key = token.tag
    feats.value = value
    feats += 1
    # Dependency label 
    feats.i = slot+2
    feats.key = token.dep
    feats.value = value
    feats += 1
    # Word, label, tag
    feats.i = slot+3
    cdef uint64_t key[3]
    key[0] = token.lex.cluster
    key[1] = token.tag
    key[2] = token.dep
    feats.key = hash64(key, sizeof(key), 0)
    feats.value = value
    feats += 1
    return feats


cdef inline FeatureC* _add_subtree(FeatureC* feats, int slot, const StateC* state, int t) nogil:
    value = 1.0
    for i in range(state.n_R(t)):
        feats = _add_token(feats, slot, state.R_(t, i+1), value)
        value *= 0.5
    slot += 4
    value = 1.0
    for i in range(state.n_L(t)):
        feats = _add_token(feats, slot, state.L_(t, i+1), value)
        value *= 0.5
    return feats


cdef inline FeatureC* _add_pos_bigram(FeatureC* feat, int slot,
        const TokenC* t1, const TokenC* t2) nogil:
    cdef uint64_t[2] key
    key[0] = t1.tag
    key[1] = t2.tag
    feat.i = slot
    feat.key = hash64(key, sizeof(key), slot)
    feat.value = 1.0
    return feat+1
 

cdef inline FeatureC* _add_pos_trigram(FeatureC* feat, int slot,
        const TokenC* t1, const TokenC* t2, const TokenC* t3) nogil:
    cdef uint64_t[3] key
    key[0] = t1.tag
    key[1] = t2.tag
    key[2] = t3.tag
    feat.i = slot
    feat.key = hash64(key, sizeof(key), slot)
    feat.value = 1.0
    return feat+1
 

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

        if cfg.get('model') == 'neural':
            model = ParserNeuralNet(cfg.hidden_layers + [moves.n_moves],
                        update_step=cfg.update_step, eta=cfg.eta, rho=cfg.rho)
        else:
            model = ParserPerceptron(get_templates(cfg.feat_set))

        if path.exists(path.join(model_dir, 'model')):
            model.load(path.join(model_dir, 'model'))
        return cls(strings, moves, model)

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

    cdef int parseC(self, TokenC* tokens, int length, int nr_feat, int nr_class) with gil:
        cdef Example py_eg = Example(nr_class=nr_class, nr_atom=CONTEXT_SIZE, nr_feat=nr_feat,
                                  widths=self.model.widths)
        cdef ExampleC* eg = py_eg.c
        state = new StateC(tokens, length)
        self.moves.initialize_state(state)
        cdef int i
        while not state.is_final():
            self.model.set_featuresC(eg, state)
            self.moves.set_valid(eg.is_valid, state)
            self.model.set_scoresC(eg.scores, eg.features, eg.nr_feat, 1)

            guess = VecVec.arg_max_if_true(eg.scores, eg.is_valid, eg.nr_class)

            action = self.moves.c[guess]
            if not eg.is_valid[guess]:
                return 1

            action.do(state, action.label)
            py_eg.reset()
        self.moves.finalize_state(state)
        for i in range(length):
            tokens[i] = state._sent[i]
        del state
        return 0
  
    def train(self, Doc tokens, GoldParse gold):
        self.moves.preprocess_gold(gold)
        cdef StateClass stcls = StateClass.init(tokens.c, tokens.length)
        self.moves.initialize_state(stcls.c)
        cdef Pool mem = Pool()
        cdef Example eg = Example(
                nr_class=self.moves.n_moves,
                widths=self.model.widths,
                nr_atom=CONTEXT_SIZE,
                nr_feat=self.model.nr_feat)
        loss = 0
        cdef Transition action
        while not stcls.is_final():
            self.model.set_featuresC(eg.c, stcls.c)
            self.model.set_scoresC(eg.c.scores, eg.c.features, eg.c.nr_feat, 1)
            self.moves.set_costs(eg.c.is_valid, eg.c.costs, stcls, gold)
            guess = VecVec.arg_max_if_true(eg.c.scores, eg.c.is_valid, eg.c.nr_class)
            assert guess >= 0
            action = self.moves.c[guess]
            action.do(stcls.c, action.label)
            
            loss += self.model.update(eg)
            eg.reset()
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
        self.parser.model.set_featuresC(self.eg.c, self.stcls.c)
        self.parser.moves.set_valid(self.eg.c.is_valid, self.stcls.c)
        self.parser.model.set_scoresC(self.eg.c.scores,
            self.eg.c.features, self.eg.c.nr_feat, 1)

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
