# cython: infer_types=True
# cython: profile=True
# cython: cdivision=True
# cython: boundscheck=False
# coding: utf-8
from __future__ import unicode_literals, print_function

from collections import Counter
import ujson
import contextlib

from libc.math cimport exp
cimport cython
cimport cython.parallel
import cytoolz
import dill

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
from thinc.neural import Model, Affine, ELU, ReLu, Maxout
from thinc.neural.ops import NumpyOps, CupyOps

from .. import util
from ..util import get_async, get_cuda_stream
from .._ml import zero_init, PrecomputableAffine, PrecomputableMaxouts
from .._ml import Tok2Vec, doc2feats, rebatch

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


cdef class precompute_hiddens:
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
    cdef int nF, nO
    cdef bint _is_synchronized
    cdef public object ops
    cdef np.ndarray _features
    cdef np.ndarray _cached
    cdef object _cuda_stream
    cdef object _bp_hiddens

    def __init__(self, batch_size, tokvecs, lower_model, cuda_stream=None, drop=0.):
        gpu_cached, bp_features = lower_model.begin_update(tokvecs, drop=drop)
        cdef np.ndarray cached
        if not isinstance(gpu_cached, numpy.ndarray):
            # Note the passing of cuda_stream here: it lets
            # cupy make the copy asynchronously.
            # We then have to block before first use.
            cached = gpu_cached.get(stream=cuda_stream)
        else:
            cached = gpu_cached
        self.nF = cached.shape[1]
        self.nO = cached.shape[2]
        self.ops = lower_model.ops
        self._features = numpy.zeros((batch_size, self.nO), dtype='f')
        self._is_synchronized = False
        self._cuda_stream = cuda_stream
        self._cached = cached
        self._bp_hiddens = bp_features

    def __call__(self, X):
        return self.begin_update(X)[0]

    def begin_update(self, token_ids, drop=0.):
        self._features.fill(0)
        if not self._is_synchronized \
        and self._cuda_stream is not None:
            self._cuda_stream.synchronize()
            self._is_synchronized = True
        # This is tricky, but (assuming GPU available);
        # - Input to forward on CPU
        # - Output from forward on CPU
        # - Input to backward on GPU!
        # - Output from backward on GPU
        cdef np.ndarray state_vector = self._features[:len(token_ids)]
        cdef np.ndarray hiddens = self._cached
        bp_hiddens = self._bp_hiddens

        cdef int[:, ::1] ids = token_ids
        self._sum_features(<float*>state_vector.data,
            <float*>hiddens.data, &ids[0,0],
            token_ids.shape[0], self.nF, self.nO)

        def backward(d_state_vector, sgd=None):
            # This will usually be on GPU
            if isinstance(d_state_vector, numpy.ndarray):
                d_state_vector = self.ops.xp.array(d_state_vector)
            d_tokens = bp_hiddens((d_state_vector, token_ids), sgd)
            return d_tokens
        return state_vector, backward

    cdef void _sum_features(self, float* output,
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


cdef class Parser:
    """
    Base class of the DependencyParser and EntityRecognizer.
    """
    @classmethod
    def Model(cls, nr_class, token_vector_width=128, hidden_width=128, **cfg):
        token_vector_width = util.env_opt('token_vector_width', token_vector_width)
        hidden_width = util.env_opt('hidden_width', hidden_width)
        lower = PrecomputableAffine(hidden_width,
                    nF=cls.nr_feature,
                    nI=token_vector_width)

        with Model.use_device('cpu'):
            upper = chain(
                        Maxout(hidden_width),
                        zero_init(Affine(nr_class))
                    )
        # TODO: This is an unfortunate hack atm!
        # Used to set input dimensions in network.
        lower.begin_training(lower.ops.allocate((500, token_vector_width)))
        upper.begin_training(upper.ops.allocate((500, hidden_width)))
        return lower, upper

    def __init__(self, Vocab vocab, moves=True, model=True, **cfg):
        """
        Create a Parser.

        Arguments:
            vocab (Vocab):
                The vocabulary object. Must be shared with documents to be processed.
                The value is set to the .vocab attribute.
            moves (TransitionSystem):
                Defines how the parse-state is created, updated and evaluated.
                The value is set to the .moves attribute unless True (default),
                in which case a new instance is created with Parser.Moves().
            model (object):
                Defines how the parse-state is created, updated and evaluated.
                The value is set to the .model attribute unless True (default),
                in which case a new instance is created with Parser.Model().
            **cfg:
                Arbitrary configuration parameters. Set to the .cfg attribute
        """
        self.vocab = vocab
        if moves is True:
            self.moves = self.TransitionSystem(self.vocab.strings, {})
        else:
            self.moves = moves
        self.cfg = cfg
        if 'actions' in self.cfg:
            for action, labels in self.cfg.get('actions', {}).items():
                for label in labels:
                    self.moves.add_action(action, label)
        self.model = model

    def __reduce__(self):
        return (Parser, (self.vocab, self.moves, self.model), None, None)

    def __call__(self, Doc doc):
        """
        Apply the parser or entity recognizer, setting the annotations onto the Doc object.

        Arguments:
            doc (Doc): The document to be processed.
        Returns:
            None
        """
        self.parse_batch([doc], doc.tensor)

    def pipe(self, docs, int batch_size=1000, int n_threads=2):
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
        cdef StateClass parse_state
        cdef Doc doc
        queue = []
        for docs in cytoolz.partition_all(batch_size, docs):
            tokvecs = self.model[0].ops.flatten([d.tensor for d in docs])
            parse_states = self.parse_batch(docs, tokvecs)
            self.set_annotations(docs, parse_states)
            yield from docs

    def parse_batch(self, docs, tokvecs):
        cuda_stream = get_cuda_stream()

        states = self.moves.init_batch(docs)
        state2vec, vec2scores = self.get_batch_model(len(states), tokvecs,
                                                     cuda_stream, 0.0)

        todo = [st for st in states if not st.is_final()]
        while todo:
            token_ids = self.get_token_ids(todo)
            vectors = state2vec(token_ids)
            scores = vec2scores(vectors)
            self.transition_batch(todo, scores)
            todo = [st for st in todo if not st.is_final()]
        return states

    def update(self, docs_tokvecs, golds, drop=0., sgd=None):
        docs, tokvecs = docs_tokvecs
        if isinstance(docs, Doc) and isinstance(golds, GoldParse):
            docs = [docs]
            golds = [golds]

        cuda_stream = get_cuda_stream()
        for gold in golds:
            self.moves.preprocess_gold(gold)

        states = self.moves.init_batch(docs)
        state2vec, vec2scores = self.get_batch_model(len(states), tokvecs, cuda_stream,
                                                      drop)

        todo = [(s, g) for s, g in zip(states, golds) if not s.is_final()]

        backprops = []
        cdef float loss = 0.
        while todo:
            states, golds = zip(*todo)

            token_ids = self.get_token_ids(states)
            vector, bp_vector = state2vec.begin_update(token_ids, drop=drop)
            scores, bp_scores = vec2scores.begin_update(vector, drop=drop)

            d_scores = self.get_batch_loss(states, golds, scores)
            d_vector = bp_scores(d_scores, sgd=sgd)

            if isinstance(self.model[0].ops, CupyOps) \
            and not isinstance(token_ids, state2vec.ops.xp.ndarray):
                # Move token_ids and d_vector to CPU, asynchronously
                backprops.append((
                    get_async(cuda_stream, token_ids),
                    get_async(cuda_stream, d_vector),
                    bp_vector
                ))
            else:
                backprops.append((token_ids, d_vector, bp_vector))
            self.transition_batch(states, scores)
            todo = [st for st in todo if not st[0].is_final()]
        # Tells CUDA to block, so our async copies complete.
        if cuda_stream is not None:
            cuda_stream.synchronize()
        d_tokvecs = state2vec.ops.allocate(tokvecs.shape)
        xp = state2vec.ops.xp # Handle for numpy/cupy
        for token_ids, d_vector, bp_vector in backprops:
            d_state_features = bp_vector(d_vector, sgd=sgd)
            active_feats = token_ids * (token_ids >= 0)
            active_feats = active_feats.reshape((token_ids.shape[0], token_ids.shape[1], 1))
            if hasattr(xp, 'scatter_add'):
                xp.scatter_add(d_tokvecs,
                    token_ids, d_state_features * active_feats)
            else:
                xp.add.at(d_tokvecs,
                    token_ids, d_state_features * active_feats)
        return d_tokvecs

    def get_batch_model(self, batch_size, tokvecs, stream, dropout):
        lower, upper = self.model
        state2vec = precompute_hiddens(batch_size, tokvecs,
                        lower, stream, drop=dropout)
        return state2vec, upper

    nr_feature = 13

    def get_token_ids(self, states):
        cdef StateClass state
        cdef int n_tokens = self.nr_feature
        ids = numpy.zeros((len(states), n_tokens), dtype='i', order='C')
        for i, state in enumerate(states):
            state.set_context_tokens(ids[i])
        return ids

    def transition_batch(self, states, float[:, ::1] scores):
        cdef StateClass state
        cdef int[500] is_valid # TODO: Unhack
        cdef float* c_scores = &scores[0, 0]
        for state in states:
            self.moves.set_valid(is_valid, state.c)
            guess = arg_max_if_valid(c_scores, is_valid, scores.shape[1])
            action = self.moves.c[guess]
            action.do(state.c, action.label)
            c_scores += scores.shape[1]

    def get_batch_loss(self, states, golds, float[:, ::1] scores):
        cdef StateClass state
        cdef GoldParse gold
        cdef Pool mem = Pool()
        cdef int i
        is_valid = <int*>mem.alloc(self.moves.n_moves, sizeof(int))
        costs = <float*>mem.alloc(self.moves.n_moves, sizeof(float))
        cdef np.ndarray d_scores = numpy.zeros((len(states), self.moves.n_moves),
                                        dtype='f', order='C')
        c_d_scores = <float*>d_scores.data
        for i, (state, gold) in enumerate(zip(states, golds)):
            memset(is_valid, 0, self.moves.n_moves * sizeof(int))
            memset(costs, 0, self.moves.n_moves * sizeof(float))
            self.moves.set_costs(is_valid, costs, state, gold)
            cpu_log_loss(c_d_scores,
                costs, is_valid, &scores[i, 0], d_scores.shape[1])
            c_d_scores += d_scores.shape[1]
        return d_scores

    def set_annotations(self, docs, states):
        cdef StateClass state
        cdef Doc doc
        for state, doc in zip(states, docs):
            self.moves.finalize_state(state.c)
            for i in range(doc.length):
                doc.c[i] = state.c._sent[i]
            self.moves.finalize_doc(doc)

    def add_label(self, label):
        for action in self.moves.action_types:
            added = self.moves.add_action(action, label)
            if added:
                # Important that the labels be stored as a list! We need the
                # order, or the model goes out of synch
                self.cfg.setdefault('extra_labels', []).append(label)

    def begin_training(self, gold_tuples, **cfg):
        if 'model' in cfg:
            self.model = cfg['model']
        actions = self.moves.get_actions(gold_parses=gold_tuples)
        for action, labels in actions.items():
            for label in labels:
                self.moves.add_action(action, label)
        if self.model is True:
            self.model = self.Model(self.moves.n_moves, **cfg)

    def use_params(self, params):
        # Can't decorate cdef class :(. Workaround.
        with self.model[0].use_params(params):
            with self.model[1].use_params(params):
                yield

    def to_disk(self, path):
        path = util.ensure_path(path)
        with (path / 'model.bin').open('wb') as file_:
            dill.dump(self.model, file_)

    def from_disk(self, path):
        path = util.ensure_path(path)
        with (path / 'model.bin').open('wb') as file_:
            self.model = dill.load(file_)

    def to_bytes(self):
        dill.dumps(self.model)

    def from_bytes(self, data):
        self.model = dill.loads(data)


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
