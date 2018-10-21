"""
MALT-style dependency parser
"""
# coding: utf-8
# cython: infer_types=True
from __future__ import unicode_literals

from collections import Counter
import ujson

cimport cython
cimport cython.parallel

import numpy.random

from cpython.ref cimport PyObject, Py_INCREF, Py_XDECREF
from cpython.exc cimport PyErr_CheckSignals
from libc.stdint cimport uint32_t, uint64_t
from libc.string cimport memset, memcpy
from libc.stdlib cimport malloc, calloc, free
from thinc.typedefs cimport weight_t, class_t, feat_t, atom_t, hash_t
from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.linalg cimport VecVec
from thinc.structs cimport SparseArrayC, FeatureC, ExampleC
from thinc.extra.eg cimport Example
from cymem.cymem cimport Pool, Address
from murmurhash.mrmr cimport hash64
from preshed.maps cimport MapStruct
from preshed.maps cimport map_get
from thinc.extra.search cimport Beam

from .._ml import link_vectors_to_models
from . import nonproj
from .. import util
from . import _parse_features
from ._parse_features cimport CONTEXT_SIZE
from ._parse_features cimport fill_context
from .stateclass cimport StateClass
from ._state cimport StateC
from .transition_system import OracleError
from .transition_system cimport TransitionSystem, Transition
from ..structs cimport TokenC
from ..tokens.doc cimport Doc
from ..strings cimport StringStore
from ..gold cimport GoldParse
from ..vocab cimport Vocab


USE_FTRL = True
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


cdef class ParserModel(AveragedPerceptron):
    @property
    def nr_templ(self):
        return self.extracter.nr_templ

    cdef int set_featuresC(self, atom_t* context, FeatureC* features,
            const StateC* state) nogil:
        fill_context(context, state)
        nr_feat = self.extracter.set_features(features, context)
        return nr_feat

    def update(self, Example eg, itn=0):
        self.time += 1
        cdef int best = arg_max_if_gold(eg.c.scores, eg.c.costs, eg.c.nr_class)
        cdef int guess = eg.guess
        if guess == best or best == -1:
            return 0.0
        cdef FeatureC feat
        cdef int clas
        cdef weight_t gradient
        for feat in eg.c.features[:eg.c.nr_feat]:
            self.update_weight(feat.key, guess, feat.value * eg.c.costs[guess])
            self.update_weight(feat.key, best, -feat.value * eg.c.costs[guess])
        return eg.c.costs[guess]


cdef class Parser:
    """
    Base class of the DependencyParser and EntityRecognizer.
    """

    @classmethod
    def Model(cls, nr_class, **cfg):
        return ParserModel(get_templates('parser')), cfg
    
    def __init__(self, Vocab vocab, moves=True, model=True, **cfg):
        """Create a Parser.

        vocab (Vocab): The vocabulary object. Must be shared with documents
            to be processed. The value is set to the `.vocab` attribute.
        moves (TransitionSystem): Defines how the parse-state is created,
            updated and evaluated. The value is set to the .moves attribute
            unless True (default), in which case a new instance is created with
            `Parser.Moves()`.
        model (object): Defines how the parse-state is created, updated and
            evaluated. The value is set to the .model attribute unless True
            (default), in which case a new instance is created with
            `Parser.Model()`.
        **cfg: Arbitrary configuration parameters. Set to the `.cfg` attribute
        """
        self.vocab = vocab
        if moves is True:
            self.moves = self.TransitionSystem(self.vocab.strings, {})
        else:
            self.moves = moves
        if 'beam_width' not in cfg:
            cfg['beam_width'] = util.env_opt('beam_width', 1)
        if 'beam_density' not in cfg:
            cfg['beam_density'] = util.env_opt('beam_density', 0.0)
        if 'pretrained_dims' not in cfg:
            cfg['pretrained_dims'] = self.vocab.vectors.data.shape[1]
        cfg.setdefault('cnn_maxout_pieces', 3)
        self.cfg = cfg
        if 'actions' in self.cfg:
            for action, labels in self.cfg.get('actions', {}).items():
                for label in labels:
                    self.moves.add_action(action, label)
        self.model = model
        if model not in (True, False, None):
            self._model = model
        self._multitasks = []

    def __reduce__(self):
        return (Parser, (self.vocab, self.moves, self.model), None, None)
    
    def __call__(self, Doc doc, beam_width=None, beam_density=None):
        """Apply the parser or entity recognizer, setting the annotations onto
        the `Doc` object.

        doc (Doc): The document to be processed.
        """
        if beam_width is None:
            beam_width = self.cfg.get('beam_width', 1)
        if beam_density is None:
            beam_density = self.cfg.get('beam_density', 0.0)
        cdef Beam beam
        if beam_width == 1:
            states, tokvecs = self.parse_batch([doc])
            self.set_annotations([doc], states, tensors=tokvecs)
            return doc
        else:
            beams, tokvecs = self.beam_parse([doc],
                                beam_width=beam_width,
                                beam_density=beam_density)
            beam = beams[0]
            output = self.moves.get_beam_annot(beam)
            state = StateClass.borrow(<StateC*>beam.at(0))
            self.set_annotations([doc], [state], tensors=tokvecs)
            _cleanup(beam)
            return output

    def parse_batch(self, docs, batch_size=1, n_threads=1):
        cdef Pool mem = Pool()
        doc_ptr = <TokenC**>mem.alloc(len(docs), sizeof(TokenC*))
        lengths = <int*>mem.alloc(len(docs), sizeof(int))
        state_ptrs = <StateC**>mem.alloc(len(docs), sizeof(StateC*))
        cdef Doc doc
        cdef StateClass state
        cdef int i
        cdef int nr_feat = self.model.nr_feat
        states = self.moves.init_batch(docs)
        for i, (doc, state) in enumerate(zip(docs, states)):
            doc_ptr[i] = doc.c
            lengths[i] = doc.length
            state_ptrs[i] = state.c
        cdef int status
        for i in range(len(docs)):
            status = self.parseC(state_ptrs[i], doc_ptr[i], lengths[i], nr_feat)
            #if status != 0:
            #    with gil:
            #        raise ParserStateError(queue[i])
            #PyErr_CheckSignals()
        return states, None

    cdef int parseC(self, StateC* state, TokenC* tokens, int length, int nr_feat) nogil:
        cdef int nr_class = self.moves.n_moves
        cdef int nr_atom = CONTEXT_SIZE
        features = <FeatureC*>calloc(sizeof(FeatureC), nr_feat)
        atoms = <atom_t*>calloc(sizeof(atom_t), CONTEXT_SIZE)
        scores = <weight_t*>calloc(sizeof(weight_t), nr_class)
        is_valid = <int*>calloc(sizeof(int), nr_class)
        cdef int i
        while not state.is_final():
            nr_feat = self._model.set_featuresC(atoms, features, state)
            self.moves.set_valid(is_valid, state)
            self._model.set_scoresC(scores, features, nr_feat)

            guess = VecVec.arg_max_if_true(scores, is_valid, nr_class)
            if guess < 0:
                return 1

            action = self.moves.c[guess]
            action.do(state, action.label)
            memset(scores, 0, sizeof(scores[0]) * nr_class)
            for i in range(nr_class):
                is_valid[i] = 1
            tokens[i] = state._sent[i]
        free(features)
        free(atoms)
        free(scores)
        free(is_valid)
        return 0

    def update(self, docs, golds, drop=0., sgd=None, losses=None):
        states = self.moves.init_batch(docs)

        cdef GoldParse gold
        for gold in golds:
            self.moves.preprocess_gold(gold)
        cdef StateClass stcls
        cdef Pool mem = Pool()
        cdef weight_t loss = 0
        cdef Transition action
        cdef double dropout_rate = self.cfg.get('dropout', drop)
        cdef FeatureC feat
        cdef int clas
        cdef int nr_class = self.moves.n_moves
        features = <FeatureC*>mem.alloc(self._model.nr_templ, sizeof(FeatureC))
        scores = <weight_t*>mem.alloc(nr_class, sizeof(weight_t))
        is_valid = <int*>mem.alloc(nr_class, sizeof(int))
        costs = <weight_t*>mem.alloc(nr_class, sizeof(weight_t))
        atoms = <atom_t*>mem.alloc(CONTEXT_SIZE, sizeof(atom_t))
        states = self.moves.init_batch(docs)
        for stcls, gold in zip(states, golds):
            while not stcls.is_final():
                memset(scores, 0, sizeof(scores[0]) * nr_class)
                memset(costs, 0, sizeof(costs[0]) * nr_class)
                for i in range(nr_class):
                    is_valid[i] = 1
                nr_feat = self._model.set_featuresC(atoms, features, stcls.c)
                dropout(features, nr_feat, dropout_rate)
                
                self.moves.set_costs(is_valid, costs, stcls, gold)
                self._model.set_scoresC(scores, features, nr_feat)
                
                self._model.time += 1
                guess = VecVec.arg_max_if_true(scores, is_valid, nr_class)
                best = arg_max_if_gold(scores, costs, nr_class)
                if guess == best or best == -1:
                    continue
                for feat in features[:nr_feat]:
                    self._model.update_weight(feat.key, guess, feat.value * costs[guess])
                    self._model.update_weight(feat.key, best, -feat.value * costs[guess])
                loss += costs[guess]

                action = self.moves.c[guess]
                action.do(stcls.c, action.label)
        return loss

    def add_label(self, label):
        for action in self.moves.action_types:
            added = self.moves.add_action(action, label)
            if added:
                # Important that the labels be stored as a list! We need the
                # order, or the model goes out of synch
                self.cfg.setdefault('extra_labels', []).append(label)
    
    def set_annotations(self, docs, states, tensors=None):
        cdef StateClass state
        cdef Doc doc
        for i, (state, doc) in enumerate(zip(states, docs)):
            self.moves.finalize_state(state.c)
            for j in range(doc.length):
                doc.c[j] = state.c._sent[j]
            if tensors is not None:
                if isinstance(doc.tensor, numpy.ndarray) \
                and not isinstance(tensors[i], numpy.ndarray):
                    doc.extend_tensor(tensors[i].get())
                else:
                    doc.extend_tensor(tensors[i])
            self.moves.finalize_doc(doc)

            for hook in self.postprocesses:
                for doc in docs:
                    hook(doc)

    @property
    def move_names(self):
        names = []
        for i in range(self.moves.n_moves):
            name = self.moves.move_name(self.moves.c[i].move, self.moves.c[i].label)
            names.append(name)
        return names

    @property
    def postprocesses(self):
        # Available for subclasses, e.g. to deprojectivize
        return []

    def begin_training(self, gold_tuples, pipeline=None, sgd=None, **cfg):
        if 'model' in cfg:
            self.model = cfg['model']
        gold_tuples = nonproj.preprocess_training_data(gold_tuples,
                                                       label_freq_cutoff=100)
        actions = self.moves.get_actions(gold_parses=gold_tuples)
        for action, labels in actions.items():
            for label in labels:
                self.moves.add_action(action, label)
        if self.model is True:
            cfg['pretrained_dims'] = self.vocab.vectors_length
            self.model, cfg = self.Model(self.moves.n_moves, **cfg)
            self._model = self.model
            if sgd is None:
                sgd = self.create_optimizer()
            self.init_multitask_objectives(gold_tuples, pipeline, sgd=sgd, **cfg)
            link_vectors_to_models(self.vocab)
            self.cfg.update(cfg)
        elif sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def init_multitask_objectives(self, gold_tuples, pipeline, **cfg):
        '''Setup models for secondary objectives, to benefit from multi-task
        learning. This method is intended to be overridden by subclasses.

        For instance, the dependency parser can benefit from sharing
        an input representation with a label prediction model. These auxiliary
        models are discarded after training.
        '''
        pass

    def preprocess_gold(self, docs_golds):
        for doc, gold in docs_golds:
            yield doc, gold

    def use_params(self, params):
        pass


cdef int dropout(FeatureC* feats, int nr_feat, float prob) except -1:
    if prob <= 0 or prob >= 1.:
        return 0
    cdef double[::1] py_probs = numpy.random.uniform(0., 1., nr_feat)
    cdef double* probs = &py_probs[0]
    for i in range(nr_feat):
        if probs[i] >= prob:
            feats[i].value /= prob
        else:
            feats[i].value = 0.


cdef class StepwiseState:
    cdef readonly StateClass stcls
    cdef readonly Example eg
    cdef readonly Doc doc
    cdef readonly GoldParse gold
    cdef readonly Parser parser

    def __init__(self, Parser parser, Doc doc, GoldParse gold=None):
        self.parser = parser
        self.doc = doc
        if gold is not None:
            self.gold = gold
            self.parser.moves.preprocess_gold(self.gold)
        else:
            self.gold = GoldParse(doc)
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

    @property
    def costs(self):
        """
        Find the action-costs for the current state.
        """
        if not self.gold:
            raise ValueError("Can't set costs: No GoldParse provided")
        self.parser.moves.set_costs(self.eg.c.is_valid, self.eg.c.costs,
                self.stcls, self.gold)
        costs = {}
        for i in range(self.parser.moves.n_moves):
            if not self.eg.c.is_valid[i]:
                continue
            transition = self.parser.moves.c[i]
            name = self.parser.moves.move_name(transition.move, transition.label)
            costs[name] = self.eg.c.costs[i]
        return costs

    def predict(self):
        self.eg.reset()
        self.eg.c.nr_feat = self.parser._model.set_featuresC(self.eg.c.atoms, self.eg.c.features,
                                                            self.stcls.c)
        self.parser.moves.set_valid(self.eg.c.is_valid, self.stcls.c)
        self.parser._model.set_scoresC(self.eg.c.scores,
            self.eg.c.features, self.eg.c.nr_feat)

        cdef Transition action = self.parser.moves.c[self.eg.guess]
        return self.parser.moves.move_name(action.move, action.label)

    def transition(self, action_name=None):
        if action_name is None:
            action_name = self.predict()
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


class ParserStateError(ValueError):
    def __init__(self, doc):
        ValueError.__init__(self,
            "Error analysing doc -- no valid actions available. This should "
            "never happen, so please report the error on the issue tracker. "
            "Here's the thread to do so --- reopen it if it's closed:\n"
            "https://github.com/spacy-io/spaCy/issues/429\n"
            "Please include the text that the parser failed on, which is:\n"
            "%s" % repr(doc.text))

cdef int arg_max_if_gold(const weight_t* scores, const weight_t* costs, int n) nogil:
    cdef int best = -1
    for i in range(n):
        if costs[i] <= 0:
            if best == -1 or scores[i] > scores[best]:
                best = i
    return best


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

def _cleanup(Beam beam):
    cdef StateC* state
    # Once parsing has finished, states in beam may not be unique. Is this
    # correct?
    seen = set()
    for i in range(beam.width):
        addr = <size_t>beam._parents[i].content
        if addr not in seen:
            state = <StateC*>addr
            del state
            seen.add(addr)
        else:
            print(i, addr)
            print(seen)
            raise Exception
        addr = <size_t>beam._states[i].content
        if addr not in seen:
            state = <StateC*>addr
            del state
            seen.add(addr)
        else:
            print(i, addr)
            print(seen)
            raise Exception
