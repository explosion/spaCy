# cython: infer_types=True
# cython: profile=True
# coding: utf-8
from __future__ import unicode_literals

from collections import Counter
import ujson

from chainer.functions.activation.softmax import Softmax as ChainerSoftmax

from cupy.cuda.stream import Stream
import cupy

from libc.math cimport exp
cimport cython
cimport cython.parallel
import cytoolz

import numpy.random
cimport numpy as np

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

from thinc.api import layerize, chain
from thinc.neural import Affine, Model, Maxout
from thinc.neural.ops import NumpyOps

from .._ml import zero_init, PrecomputableAffine, PrecomputableMaxouts
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
from ..attrs cimport TAG, DEP


def get_templates(*args, **kwargs):
    return []

USE_FTRL = True
DEBUG = False
def set_debug(val):
    global DEBUG
    DEBUG = val


def get_greedy_model_for_batch(batch_size, tokvecs, lower_model, cuda_stream=None):
    '''Allow a model to be "primed" by pre-computing input features in bulk.

    This is used for the parser, where we want to take a batch of documents,
    and compute vectors for each (token, position) pair. These vectors can then
    be reused, especially for beam-search.

    Let's say we're using 12 features for each state, e.g. word at start of
    buffer, three words on stack, their children, etc. In the normal arc-eager
    system, a document of length N is processed in 2*N states. This means we'll
    create 2*N*12 feature vectors --- but if we pre-compute, we only need
    N*12 vector computations. The saving for beam-search is much better:
    if we have a beam of k, we'll normally make 2*N*12*K computations --
    so we can save the factor k. This also gives a nice CPU/GPU division:
    we can do all our hard maths up front, packed into large multiplications,
    and do the hard-to-program parsing on the CPU.
    '''
    gpu_cached, bp_features = lower_model.begin_update(tokvecs, drop=0.)
    cdef np.ndarray cached
    if not isinstance(gpu_cached, numpy.ndarray):
        cached = gpu_cached.get(stream=cuda_stream)
    else:
        cached = gpu_cached
    nF = gpu_cached.shape[1]
    nP = gpu_cached.shape[3]
    ops = lower_model.ops
    features = numpy.zeros((batch_size, cached.shape[2], nP), dtype='f')
    synchronized = False

    def forward(token_ids, drop=0.):
        nonlocal synchronized
        if not synchronized and cuda_stream is not None:
            cuda_stream.synchronize()
            synchronized = True
        # This is tricky, but:
        # - Input to forward on CPU
        # - Output from forward on CPU
        # - Input to backward on GPU!
        # - Output from backward on GPU
        nonlocal features
        features = features[:len(token_ids)]
        features.fill(0)
        cdef float[:, :, ::1] feats = features
        cdef int[:, ::1] ids = token_ids
        _sum_features(<float*>&feats[0,0,0],
            <float*>cached.data, &ids[0,0],
            token_ids.shape[0], nF, cached.shape[2]*nP)

        if nP >= 2:
            best, which = ops.maxout(features)
        else:
            best = features.reshape((features.shape[0], features.shape[1]))
            which = None

        def backward(d_best, sgd=None):
            # This will usually be on GPU
            if isinstance(d_best, numpy.ndarray):
                d_best = ops.xp.array(d_best)
            if nP >= 2:
                d_features = ops.backprop_maxout(d_best, which, nP)
            else:
                d_features = d_best.reshape((d_best.shape[0], d_best.shape[1], 1))
            d_tokens = bp_features((d_features, token_ids), sgd)
            return d_tokens

        return best, backward

    return forward


cdef void _sum_features(float* output,
        const float* cached, const int* token_ids, int B, int F, int O) nogil:
    cdef int idx, b, f, i
    cdef const float* feature
    for b in range(B):
        for f in range(F):
            if token_ids[f] < 0:
                continue
            idx = token_ids[f] * F * O + f*O
            feature = &cached[idx]
            for i in range(O):
                output[i] += feature[i]
        output += O
        token_ids += F


def get_batch_loss(TransitionSystem moves, states, golds, float[:, ::1] scores):
    cdef StateClass state
    cdef GoldParse gold
    cdef Pool mem = Pool()
    cdef int i
    is_valid = <int*>mem.alloc(moves.n_moves, sizeof(int))
    costs = <float*>mem.alloc(moves.n_moves, sizeof(float))
    cdef np.ndarray d_scores = numpy.zeros((len(states), moves.n_moves), dtype='f')
    c_d_scores = <float*>d_scores.data
    for i, (state, gold) in enumerate(zip(states, golds)):
        memset(is_valid, 0, moves.n_moves * sizeof(int))
        memset(costs, 0, moves.n_moves * sizeof(float))
        moves.set_costs(is_valid, costs, state, gold)
        cpu_log_loss(c_d_scores, costs, is_valid, &scores[i, 0], d_scores.shape[1])
        c_d_scores += d_scores.shape[1]
    return d_scores


cdef void cpu_log_loss(float* d_scores,
        const float* costs, const int* is_valid, const float* scores,
        int O) nogil:
    """Do multi-label log loss"""
    cdef double max_, gmax, Z, gZ
    best = arg_max_if_gold(scores, costs, is_valid, O)
    guess = arg_max_if_valid(scores, is_valid, O)
    Z = 1e-10
    gZ = 1e-10
    max_ = scores[guess]
    gmax = scores[best]
    for i in range(O):
        if is_valid[i]:
            Z += exp(scores[i] - max_)
            if costs[i] <= costs[best]:
                gZ += exp(scores[i] - gmax)
    for i in range(O):
        if not is_valid[i]:
            d_scores[i] = 0.
        elif costs[i] <= costs[best]:
            d_scores[i] = (exp(scores[i]-max_) / Z) - (exp(scores[i]-gmax)/gZ)
        else:
            d_scores[i] = exp(scores[i]-max_) / Z


cdef void cpu_regression_loss(float* d_scores,
        const float* costs, const int* is_valid, const float* scores,
        int O) nogil:
    cdef float eps = 2.
    best = arg_max_if_gold(scores, costs, is_valid, O)
    for i in range(O):
        if not is_valid[i]:
            d_scores[i] = 0.
        elif scores[i] < scores[best]:
            d_scores[i] = 0.
        else:
            # I doubt this is correct?
            # Looking for something like Huber loss
            diff = scores[i] - -costs[i]
            if diff > eps:
                d_scores[i] = eps
            elif diff < -eps:
                d_scores[i] = -eps
            else:
                d_scores[i] = diff


def init_states(TransitionSystem moves, docs):
    cdef Doc doc
    cdef StateClass state
    offsets = []
    states = []
    offset = 0
    for i, doc in enumerate(docs):
        state = StateClass.init(doc.c, doc.length)
        moves.initialize_state(state.c)
        states.append(state)
        offsets.append(offset)
        offset += len(doc)
    return states, offsets


def extract_token_ids(states, offsets=None, nF=1, nB=0, nS=2, nL=0, nR=0):
    cdef StateClass state
    cdef int n_tokens = states[0].nr_context_tokens(nF, nB, nS, nL, nR)
    ids = numpy.zeros((len(states), n_tokens), dtype='i')
    if offsets is None:
        offsets = [0] * len(states)
    for i, (state, offset) in enumerate(zip(states, offsets)):
        state.set_context_tokens(ids[i], nF, nB, nS, nL, nR)
        ids[i] += (ids[i] >= 0) * offset
    return ids


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
            self.model, self.feature_maps = self.build_model(**cfg)
        else:
            self.model, self.feature_maps = model
        self.cfg = cfg

    def __reduce__(self):
        return (Parser, (self.vocab, self.moves, self.model), None, None)

    def build_model(self,
            hidden_width=128, token_vector_width=96, nr_vector=1000,
            nF=1, nB=1, nS=1, nL=1, nR=1, **cfg):
        nr_context_tokens = StateClass.nr_context_tokens(nF, nB, nS, nL, nR)
        with Model.use_device('cpu'):
            upper = chain(
                        Maxout(token_vector_width),
                        zero_init(Affine(self.moves.n_moves, token_vector_width)))
        assert isinstance(upper.ops, NumpyOps)
        lower = PrecomputableMaxouts(token_vector_width, nF=nr_context_tokens, nI=token_vector_width,
                                     pieces=cfg.get('maxout_pieces', 1))
        upper.begin_training(upper.ops.allocate((500, token_vector_width)))
        lower.begin_training(lower.ops.allocate((500, token_vector_width)))
        return upper, lower

    def __call__(self, Doc tokens):
        """
        Apply the parser or entity recognizer, setting the annotations onto the Doc object.

        Arguments:
            doc (Doc): The document to be processed.
        Returns:
            None
        """
        self.parse_batch([tokens])

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
        queue = []
        for doc in stream:
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

    def parse_batch(self, docs_tokvecs):
        cdef:
            int nC
            Doc doc
            StateClass state
            np.ndarray py_scores
            int[500] is_valid # Hacks for now

        cuda_stream = Stream()
        docs, tokvecs = docs_tokvecs
        lower_model = get_greedy_model_for_batch(len(docs), tokvecs, self.feature_maps,
                                                 cuda_stream)
        upper_model = self.model

        states, offsets = init_states(self.moves, docs)
        all_states = list(states)
        todo = [st for st in zip(states, offsets) if not st[0].py_is_final()]

        while todo:
            states, offsets = zip(*todo)
            token_ids = extract_token_ids(states, offsets=offsets)

            py_scores = upper_model(lower_model(token_ids)[0])
            scores = <float*>py_scores.data
            nC = py_scores.shape[1]
            for state, offset in zip(states, offsets):
                self.moves.set_valid(is_valid, state.c)
                guess = arg_max_if_valid(scores, is_valid, nC)
                action = self.moves.c[guess]
                action.do(state.c, action.label)
                scores += nC
            todo = [st for st in todo if not st[0].py_is_final()]

        for state, doc in zip(all_states, docs):
            self.moves.finalize_state(state.c)
            for i in range(doc.length):
                doc.c[i] = state.c._sent[i]
            self.moves.finalize_doc(doc)

    def update(self, docs_tokvecs, golds, drop=0., sgd=None):
        cdef:
            int nC
            int[500] is_valid # Hack for now
            Doc doc
            StateClass state
            np.ndarray scores

        docs, tokvecs = docs_tokvecs
        cuda_stream = Stream()
        if isinstance(docs, Doc) and isinstance(golds, GoldParse):
            return self.update(([docs], tokvecs), [golds], drop=drop)
        for gold in golds:
            self.moves.preprocess_gold(gold)

        states, offsets = init_states(self.moves, docs)

        todo = zip(states, offsets, golds)
        todo = filter(lambda sp: not sp[0].py_is_final(), todo)

        lower_model = get_greedy_model_for_batch(len(todo),
                        tokvecs, self.feature_maps, cuda_stream=cuda_stream)
        upper_model = self.model
        d_tokens = self.feature_maps.ops.allocate(tokvecs.shape)
        backprops = []
        n_tokens = tokvecs.shape[0]
        nF = self.feature_maps.nF
        while todo:
            states, offsets, golds = zip(*todo)

            token_ids = extract_token_ids(states, offsets=offsets)
            lower, bp_lower = lower_model(token_ids)
            scores, bp_scores = upper_model.begin_update(lower)

            d_scores = get_batch_loss(self.moves, states, golds, scores)
            d_lower = bp_scores(d_scores, sgd=sgd)

            gpu_tok_ids = cupy.ndarray(token_ids.shape, dtype='i')
            gpu_d_lower = cupy.ndarray(d_lower.shape, dtype='f')
            gpu_tok_ids.set(token_ids, stream=cuda_stream)
            gpu_d_lower.set(d_lower, stream=cuda_stream)
            backprops.append((gpu_tok_ids, gpu_d_lower, bp_lower))

            c_scores = <float*>scores.data
            for state in states:
                self.moves.set_valid(is_valid, state.c)
                guess = arg_max_if_valid(c_scores, is_valid, scores.shape[1])
                action = self.moves.c[guess]
                action.do(state.c, action.label)
                c_scores += scores.shape[1]

            todo = filter(lambda sp: not sp[0].py_is_final(), todo)
        # This tells CUDA to block --- so we know our copies are complete.
        cuda_stream.synchronize()
        for token_ids, d_lower, bp_lower in backprops:
            d_state_features = bp_lower(d_lower, sgd=sgd)
            active_feats = token_ids * (token_ids >= 0)
            active_feats = active_feats.reshape((token_ids.shape[0], token_ids.shape[1], 1))
            if hasattr(self.feature_maps.ops.xp, 'scatter_add'):
                self.feature_maps.ops.xp.scatter_add(d_tokens,
                    token_ids, d_state_features * active_feats)
            else:
                self.model.ops.xp.add.at(d_tokens,
                    token_ids, d_state_features * active_feats)
        return d_tokens

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
        #self.eg.c.nr_feat = self.parser.model.set_featuresC(self.eg.c.atoms, self.eg.c.features,
        #                                                    self.stcls.c)
        self.parser.moves.set_valid(self.eg.c.is_valid, self.stcls.c)
        #self.parser.model.set_scoresC(self.eg.c.scores,
        #    self.eg.c.features, self.eg.c.nr_feat)

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


cdef int arg_max_if_gold(const weight_t* scores, const weight_t* costs, const int* is_valid, int n) nogil:
    # Find minimum cost
    cdef float cost = 1
    for i in range(n):
        if is_valid[i] and costs[i] < cost:
            cost = costs[i]
    # Now find best-scoring with that cost
    cdef int best = -1
    for i in range(n):
        if costs[i] <= cost and is_valid[i]:
            if best == -1 or scores[i] > scores[best]:
                best = i
    return best


cdef int arg_max_if_valid(const weight_t* scores, const int* is_valid, int n) nogil:
    cdef int best = -1
    for i in range(n):
        if is_valid[i] >= 1:
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
