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

from . import _parse_features
from ._parse_features cimport CONTEXT_SIZE
from ._parse_features cimport fill_context
from .stateclass cimport StateClass
from ._state cimport StateC
from .nonproj import PseudoProjectivity
from .transition_system import OracleError
from .transition_system cimport TransitionSystem, Transition
from ..structs cimport TokenC
from ..tokens.doc cimport Doc
from ..strings cimport StringStore
from ..gold cimport GoldParse


USE_FTRL = True
DEBUG = False
def set_debug(val):
    global DEBUG
    DEBUG = val


@layerize
def get_context_tokens(states, drop=0.):
    for state in states:
        context[i, 0] = state.B(0)
        context[i, 1] = state.S(0)
        context[i, 2] = state.S(1)
        context[i, 3] = state.L(state.S(0), 1)
        context[i, 4] = state.L(state.S(0), 2)
        context[i, 5] = state.R(state.S(0), 1)
        context[i, 6] = state.R(state.S(0), 2)
    return (context, states), None


def extract_features(attrs):
    def forward(contexts_states, drop=0.):
        contexts, states = contexts_states
        for i, state in enumerate(states):
            for j, tok_i in enumerate(contexts[i]):
                token = state.get_token(tok_i)
                for k, attr in enumerate(attrs):
                    output[i, j, k] = getattr(token, attr)
        return output, None
    return layerize(forward)


def build_tok2vec(lang, width, depth, embed_size):
    cols = [LEX_ID, PREFIX, SUFFIX, SHAPE]
    static = StaticVectors('en', width, column=cols.index(LEX_ID))
    prefix = HashEmbed(width, embed_size, column=cols.index(PREFIX))
    suffix = HashEmbed(width, embed_size, column=cols.index(SUFFIX))
    shape = HashEmbed(width, embed_size, column=cols.index(SHAPE))
    with Model.overload_operaters('>>': chain, '|': concatenate, '+': add):
        tok2vec = (
            extract_features(cols)
            >> (static | prefix | suffix | shape)
            >> (ExtractWindow(nW=1) >> Maxout(width)) ** depth
        )
    return tok2vec


def build_parse2vec(width, embed_size):
    cols = [TAG, DEP]
    tag_vector = HashEmbed(width, 1000, column=cols.index(TAG))
    dep_vector = HashEmbed(width, 1000, column=cols.index(DEP))
    with Model.overload_operaters('>>': chain):
        model = (
            extract_features([TAG, DEP])
            >> (tag_vector | dep_vector)
        )
    return model
 

def build_model(get_contexts, tok2vec, parse2vec, width, depth, nr_class):
    with Model.overload_operaters('>>': chain):
        model = (
            get_contexts
            >> (tok2vec | parse2vec)
            >> Maxout(width) ** depth
            >> Softmax(nr_class)
        )
    return model


cdef class Parser:
    """
    Base class of the DependencyParser and EntityRecognizer.
    """
    @classmethod
    def load(cls, path, Vocab vocab, TransitionSystem=None, require=False, **cfg):
        """
        Load the statistical model from the supplied path.

        Arguments:
            path (Path):
                The path to load from.
            vocab (Vocab):
                The vocabulary. Must be shared by the documents to be processed.
            require (bool):
                Whether to raise an error if the files are not found.
        Returns (Parser):
            The newly constructed object.
        """
        with (path / 'config.json').open() as file_:
            cfg = ujson.load(file_)
        self = cls(vocab, TransitionSystem=TransitionSystem, model=None, **cfg)
        if (path / 'model').exists():
            self.model.load(str(path / 'model'))
        elif require:
            raise IOError(
                "Required file %s/model not found when loading" % str(path))
        return self

    def __init__(self, Vocab vocab, TransitionSystem=None, model=None, **cfg):
        """
        Create a Parser.

        Arguments:
            vocab (Vocab):
                The vocabulary object. Must be shared with documents to be processed.
            model (thinc Model):
                The statistical model.
        Returns (Parser):
            The newly constructed object.
        """
        if TransitionSystem is None:
            TransitionSystem = self.TransitionSystem
        self.vocab = vocab
        cfg['actions'] = TransitionSystem.get_actions(**cfg)
        self.moves = TransitionSystem(vocab.strings, cfg['actions'])
        if model is None:
            model = self.build_model(**cfg)
        self.model = model
        self.cfg = cfg
    
    def __reduce__(self):
        return (Parser, (self.vocab, self.moves, self.model), None, None)

    def __call__(self, Doc tokens):
        """
        Apply the parser or entity recognizer, setting the annotations onto the Doc object.

        Arguments:
            doc (Doc): The document to be processed.
        Returns:
            None
        """
        self.parse_batch([tokens])
        self.moves.finalize_doc(tokens)

    def parse_batch(self, docs):
        states = self._init_states(docs)
        todo = list(states)
        nr_class = self.moves.n_moves
        while todo:
            scores = self.model.predict(todo)
            self._validate_batch(is_valid, scores, states)
            for state, guess in zip(todo, scores.argmax(axis=1)):
                action = self.moves.c[guess]
                action.do(state, action.label)
            todo = [state for state in todo if not state.is_final()]
        for state, doc in zip(states, docs):
            self.moves.finalize_state(state, doc)

    def pipe(self, stream, int batch_size=1000, int n_threads=2):
        """
        Process a stream of documents.

        Arguments:
            stream: The sequence of documents to process.
            batch_size (int):
                The number of documents to accumulate into a working set.
            n_threads (int):
                The number of threads with which to work on the buffer in parallel.
        Yields (Doc): Documents, in order.
        """
        cdef Pool mem = Pool()
        cdef int* lengths = <int*>mem.alloc(batch_size, sizeof(int))
        cdef Doc doc
        cdef int i
        cdef int nr_feat = self.model.nr_feat
        cdef int status
        queue = []
        for doc in stream:
            doc_ptr[len(queue)] = doc.c
            lengths[len(queue)] = doc.length
            queue.append(doc)
            if len(queue) == batch_size:
                self.parse_batch(queue)
                for doc in queue:
                    self.moves.finalize_doc(doc)
                    yield doc
                queue = []
        if queue:
            self.parse_batch(queue)
            for doc in queue:
                self.moves.finalize_doc(doc)
                yield doc

    def update(self, docs, golds, drop=0., sgd=None):
        if isinstance(docs, Doc) and isinstance(golds, GoldParse):
            return self.update([docs], [golds], drop=drop)
        states = self._init_states(docs)
        nr_class = self.moves.n_moves
        while states:
            scores, finish_update = self.model.begin_update(states, drop=drop)
            self._validate_batch(is_valid, scores, states)
            for i, state in enumerate(states):
                self.moves.set_costs(costs[i], is_valid, state, golds[i])
            
            self._transition_batch(states, scores)
            self._set_gradient(gradients, scores, costs)
            finish_update(gradients, sgd=sgd)
            gradients.fill(0)
            
            states = [state for state in states if not state.is_final()]
            gradients = gradients[:len(states)]
            costs = costs[:len(states)]
        return 0

    def _validate_batch(self, is_valid, scores, states):
        for i, state in enumerate(states):
            self.moves.set_valid(is_valid, state)
            for j in range(self.moves.n_moves):
                if not is_valid[j]:
                    scores[i, j] = 0

    def _transition_batch(self, states, scores):
        for state, guess in zip(states, scores.argmax(axis=1)):
            action = self.moves.c[guess]
            action.do(state, action.label)

    def _init_states(self, docs):
        states = []
        cdef Doc doc
        for i, doc in enumerate(docs):
            state = StateClass.init(doc)
            self.moves.initialize_state(state)
        return states

    def _set_gradient(self, gradients, scores, costs):
        """Do multi-label log loss"""
        cdef double Z, gZ, max_, g_max
        maxes = scores.max(axis=1)
        g_maxes = (scores * costs <= 0).max(axis=1)
        exps = (scores-maxes).exp()
        g_exps = (g_scores-g_maxes).exp()

        Zs = exps.sum(axis=1)
        gZs = g_exps.sum(axis=1)
        logprob = exps / Zs
        g_logprob = g_exps / gZs
        gradients[:] = logprob - g_logprob

    def step_through(self, Doc doc, GoldParse gold=None):
        """
        Set up a stepwise state, to introspect and control the transition sequence.

        Arguments:
            doc (Doc): The document to step through.
            gold (GoldParse): Optional gold parse
        Returns (StepwiseState):
            A state object, to step through the annotation process.
        """
        return StepwiseState(self, doc, gold=gold)

    def from_transition_sequence(self, Doc doc, sequence):
        """Control the annotations on a document by specifying a transition sequence
        to follow.

        Arguments:
            doc (Doc): The document to annotate.
            sequence: A sequence of action names, as unicode strings.
        Returns: None
        """
        with self.step_through(doc) as stepwise:
            for transition in sequence:
                stepwise.transition(transition)

    def add_label(self, label):
        # Doesn't set label into serializer -- subclasses override it to do that.
        for action in self.moves.action_types:
            added = self.moves.add_action(action, label)
            if added:
                # Important that the labels be stored as a list! We need the
                # order, or the model goes out of synch
                self.cfg.setdefault('extra_labels', []).append(label)


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
        self.eg.c.nr_feat = self.parser.model.set_featuresC(self.eg.c.atoms, self.eg.c.features,
                                                            self.stcls.c)
        self.parser.moves.set_valid(self.eg.c.is_valid, self.stcls.c)
        self.parser.model.set_scoresC(self.eg.c.scores,
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
