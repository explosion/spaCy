# cython: infer_types=True
# cython: cdivision=True
# cython: boundscheck=False
# coding: utf-8
from __future__ import unicode_literals, print_function

from collections import OrderedDict
import numpy
cimport cython.parallel
import numpy.random
cimport numpy as np
from libc.math cimport exp
from libcpp.vector cimport vector
from libc.string cimport memset, memcpy
from libc.stdlib cimport calloc, free, realloc
from cymem.cymem cimport Pool
from thinc.typedefs cimport weight_t, class_t, hash_t
from thinc.extra.search cimport Beam
from thinc.api import chain, clone
from thinc.v2v import Model, Maxout, Affine
from thinc.misc import LayerNorm
from thinc.neural.ops import CupyOps
from thinc.neural.util import get_array_module
from thinc.linalg cimport Vec, VecVec
cimport blis.cy

from .._ml import zero_init, PrecomputableAffine, Tok2Vec, flatten
from .._ml import link_vectors_to_models, create_default_optimizer
from ..compat import copy_array
from ..tokens.doc cimport Doc
from ..gold cimport GoldParse
from ..errors import Errors, TempErrors
from .. import util
from .stateclass cimport StateClass
from .transition_system cimport Transition
from . import _beam_utils
from . import nonproj


cdef WeightsC get_c_weights(model) except *:
    cdef WeightsC output
    cdef precompute_hiddens state2vec = model.state2vec
    output.feat_weights = state2vec.get_feat_weights()
    output.feat_bias = <const float*>state2vec.bias.data
    cdef np.ndarray vec2scores_W = model.vec2scores.W
    cdef np.ndarray vec2scores_b = model.vec2scores.b
    cdef np.ndarray class_mask = model._class_mask
    output.hidden_weights = <const float*>vec2scores_W.data
    output.hidden_bias = <const float*>vec2scores_b.data
    output.seen_classes = <const float*>class_mask.data
    return output


cdef SizesC get_c_sizes(model, int batch_size) except *:
    cdef SizesC output
    output.states = batch_size
    output.classes = model.vec2scores.nO
    output.hiddens = model.state2vec.nO
    output.pieces = model.state2vec.nP
    output.feats = model.state2vec.nF
    output.embed_width = model.tokvecs.shape[1]
    return output


cdef void resize_activations(ActivationsC* A, SizesC n) nogil:
    if n.states <= A._max_size:
        A._curr_size = n.states
        return
    if A._max_size == 0:
        A.token_ids = <int*>calloc(n.states * n.feats, sizeof(A.token_ids[0]))
        A.scores = <float*>calloc(n.states * n.classes, sizeof(A.scores[0]))
        A.unmaxed = <float*>calloc(n.states * n.hiddens * n.pieces, sizeof(A.unmaxed[0]))
        A.hiddens = <float*>calloc(n.states * n.hiddens, sizeof(A.hiddens[0]))
        A.is_valid = <int*>calloc(n.states * n.classes, sizeof(A.is_valid[0]))
        A._max_size = n.states
    else:
        A.token_ids = <int*>realloc(A.token_ids,
            n.states * n.feats * sizeof(A.token_ids[0]))
        A.scores = <float*>realloc(A.scores,
            n.states * n.classes * sizeof(A.scores[0]))
        A.unmaxed = <float*>realloc(A.unmaxed,
            n.states * n.hiddens * n.pieces * sizeof(A.unmaxed[0]))
        A.hiddens = <float*>realloc(A.hiddens,
            n.states * n.hiddens * sizeof(A.hiddens[0]))
        A.is_valid = <int*>realloc(A.is_valid,
            n.states * n.classes * sizeof(A.is_valid[0]))
        A._max_size = n.states
    A._curr_size = n.states


cdef void predict_states(ActivationsC* A, StateC** states,
        const WeightsC* W, SizesC n) nogil:
    resize_activations(A, n)
    memset(A.unmaxed, 0, n.states * n.hiddens * n.pieces * sizeof(float))
    memset(A.hiddens, 0, n.states * n.hiddens * sizeof(float))
    for i in range(n.states):
        states[i].set_context_tokens(&A.token_ids[i*n.feats], n.feats)
    sum_state_features(A.unmaxed,
        W.feat_weights, A.token_ids, n.states, n.feats, n.hiddens * n.pieces)
    for i in range(n.states):
        VecVec.add_i(&A.unmaxed[i*n.hiddens*n.pieces],
            W.feat_bias, 1., n.hiddens * n.pieces)
        for j in range(n.hiddens):
            index = i * n.hiddens * n.pieces + j * n.pieces
            which = Vec.arg_max(&A.unmaxed[index], n.pieces)
            A.hiddens[i*n.hiddens + j] = A.unmaxed[index + which]
    memset(A.scores, 0, n.states * n.classes * sizeof(float))
    cdef double one = 1.0
    # Compute hidden-to-output
    blis.cy.gemm(blis.cy.NO_TRANSPOSE, blis.cy.TRANSPOSE,
        n.states, n.classes, n.hiddens, one,
        <float*>A.hiddens, n.hiddens, 1,
        <float*>W.hidden_weights, n.hiddens, 1,
        one,
        <float*>A.scores, n.classes, 1)
    # Add bias
    for i in range(n.states):
        VecVec.add_i(&A.scores[i*n.classes],
            W.hidden_bias, 1., n.classes)
    # Set unseen classes to minimum value
    i = 0
    min_ = A.scores[0]
    for i in range(1, n.states * n.classes):
        if A.scores[i] < min_:
            min_ = A.scores[i]
    for i in range(n.states):
        for j in range(n.classes):
            if not W.seen_classes[j]:
                A.scores[i*n.classes+j] = min_


cdef void sum_state_features(float* output,
        const float* cached, const int* token_ids, int B, int F, int O) nogil:
    cdef int idx, b, f, i
    cdef const float* feature
    padding = cached
    cached += F * O
    cdef int id_stride = F*O
    cdef float one = 1.
    for b in range(B):
        for f in range(F):
            if token_ids[f] < 0:
                feature = &padding[f*O]
            else:
                idx = token_ids[f] * id_stride + f*O
                feature = &cached[idx]
            blis.cy.axpyv(blis.cy.NO_CONJUGATE, O, one,
                <float*>feature, 1,
                &output[b*O], 1)
        token_ids += F


cdef void cpu_log_loss(float* d_scores,
        const float* costs, const int* is_valid, const float* scores,
        int O) nogil:
    """Do multi-label log loss"""
    cdef double max_, gmax, Z, gZ
    best = arg_max_if_gold(scores, costs, is_valid, O)
    guess = Vec.arg_max(scores, O)
    if best == -1 or guess == -1:
        # These shouldn't happen, but if they do, we want to make sure we don't
        # cause an OOB access.
        return
    Z = 1e-10
    gZ = 1e-10
    max_ = scores[guess]
    gmax = scores[best]
    for i in range(O):
        Z += exp(scores[i] - max_)
        if costs[i] <= costs[best]:
            gZ += exp(scores[i] - gmax)
    for i in range(O):
        if costs[i] <= costs[best]:
            d_scores[i] = (exp(scores[i]-max_) / Z) - (exp(scores[i]-gmax)/gZ)
        else:
            d_scores[i] = exp(scores[i]-max_) / Z


cdef int arg_max_if_gold(const weight_t* scores, const weight_t* costs,
        const int* is_valid, int n) nogil:
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


class ParserModel(Model):
    def __init__(self, tok2vec, lower_model, upper_model, unseen_classes=None):
        Model.__init__(self)
        self._layers = [tok2vec, lower_model, upper_model]
        self.unseen_classes = set()
        if unseen_classes:
            for class_ in unseen_classes:
                self.unseen_classes.add(class_)

    def begin_update(self, docs, drop=0.):
        step_model = ParserStepModel(docs, self._layers, drop=drop,
                        unseen_classes=self.unseen_classes)
        def finish_parser_update(golds, sgd=None):
            step_model.make_updates(sgd)
            return None
        return step_model, finish_parser_update

    def resize_output(self, new_output):
        if new_output == self.upper.nO:
            return
        smaller = self.upper

        with Model.use_device('cpu'):
            larger = Affine(new_output, smaller.nI)
        larger.W.fill(0.0)
        larger.b.fill(0.0)
        # It seems very unhappy if I pass these as smaller.W?
        # Seems to segfault. Maybe it's a descriptor protocol thing?
        smaller_W = smaller.W
        larger_W = larger.W
        smaller_b = smaller.b
        larger_b = larger.b
        # Weights are stored in (nr_out, nr_in) format, so we're basically
        # just adding rows here.
        larger_W[:smaller.nO] = smaller_W
        larger_b[:smaller.nO] = smaller_b
        self._layers[-1] = larger
        for i in range(smaller.nO, new_output):
            self.unseen_classes.add(i)

    def begin_training(self, X, y=None):
        self.lower.begin_training(X, y=y)

    @property
    def tok2vec(self):
        return self._layers[0]

    @property
    def lower(self):
        return self._layers[1]

    @property
    def upper(self):
        return self._layers[2]


class ParserStepModel(Model):
    def __init__(self, docs, layers, unseen_classes=None, drop=0.):
        self.tokvecs, self.bp_tokvecs = layers[0].begin_update(docs, drop=drop)
        self.state2vec = precompute_hiddens(len(docs), self.tokvecs, layers[1],
                                            drop=drop)
        self.vec2scores = layers[-1]
        self.cuda_stream = util.get_cuda_stream()
        self.backprops = []
        self._class_mask = numpy.zeros((self.vec2scores.nO,), dtype='f')
        self._class_mask.fill(1)
        if unseen_classes is not None:
            for class_ in unseen_classes:
                self._class_mask[class_] = 0.

    @property
    def nO(self):
        return self.state2vec.nO

    def class_is_unseen(self, class_):
        return self._class_mask[class_]

    def mark_class_unseen(self, class_):
        self._class_mask[class_] = 0

    def mark_class_seen(self, class_):
        self._class_mask[class_] = 1

    def begin_update(self, states, drop=0.):
        token_ids = self.get_token_ids(states)
        vector, get_d_tokvecs = self.state2vec.begin_update(token_ids, drop=0.0)
        mask = self.vec2scores.ops.get_dropout_mask(vector.shape, drop)
        if mask is not None:
            vector *= mask
        scores, get_d_vector = self.vec2scores.begin_update(vector, drop=drop)
        # If the class is unseen, make sure its score is minimum
        scores[:, self._class_mask == 0] = numpy.nanmin(scores)

        def backprop_parser_step(d_scores, sgd=None):
            # Zero vectors for unseen classes
            d_scores *= self._class_mask
            d_vector = get_d_vector(d_scores, sgd=sgd)
            if mask is not None:
                d_vector *= mask
            if isinstance(self.state2vec.ops, CupyOps) \
            and not isinstance(token_ids, self.state2vec.ops.xp.ndarray):
                # Move token_ids and d_vector to GPU, asynchronously
                self.backprops.append((
                    util.get_async(self.cuda_stream, token_ids),
                    util.get_async(self.cuda_stream, d_vector),
                    get_d_tokvecs
                ))
            else:
                self.backprops.append((token_ids, d_vector, get_d_tokvecs))
            return None
        return scores, backprop_parser_step

    def get_token_ids(self, batch):
        states = _beam_utils.collect_states(batch)
        cdef StateClass state
        states = [state for state in states if not state.is_final()]
        cdef np.ndarray ids = numpy.zeros((len(states), self.state2vec.nF),
                                          dtype='i', order='C')
        ids.fill(-1)
        c_ids = <int*>ids.data
        for state in states:
            state.c.set_context_tokens(c_ids, ids.shape[1])
            c_ids += ids.shape[1]
        return ids

    def make_updates(self, sgd):
        # Tells CUDA to block, so our async copies complete.
        if self.cuda_stream is not None:
            self.cuda_stream.synchronize()
        # Add a padding vector to the d_tokvecs gradient, so that missing
        # values don't affect the real gradient.
        d_tokvecs = self.ops.allocate((self.tokvecs.shape[0]+1, self.tokvecs.shape[1]))
        for ids, d_vector, bp_vector in self.backprops:
            d_state_features = bp_vector((d_vector, ids), sgd=sgd)
            ids = ids.flatten()
            d_state_features = d_state_features.reshape(
                (ids.size, d_state_features.shape[2]))
            self.ops.scatter_add(d_tokvecs, ids,
                d_state_features)
        # Padded -- see update()
        self.bp_tokvecs(d_tokvecs[:-1], sgd=sgd)
        return d_tokvecs


cdef class precompute_hiddens:
    """Allow a model to be "primed" by pre-computing input features in bulk.

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
    """
    cdef readonly int nF, nO, nP
    cdef bint _is_synchronized
    cdef public object ops
    cdef np.ndarray _features
    cdef np.ndarray _cached
    cdef np.ndarray bias
    cdef object _cuda_stream
    cdef object _bp_hiddens

    def __init__(self, batch_size, tokvecs, lower_model, cuda_stream=None,
                 drop=0.):
        gpu_cached, bp_features = lower_model.begin_update(tokvecs, drop=drop)
        cdef np.ndarray cached
        if not isinstance(gpu_cached, numpy.ndarray):
            # Note the passing of cuda_stream here: it lets
            # cupy make the copy asynchronously.
            # We then have to block before first use.
            cached = gpu_cached.get(stream=cuda_stream)
        else:
            cached = gpu_cached
        if not isinstance(lower_model.b, numpy.ndarray):
            self.bias = lower_model.b.get()
        else:
            self.bias = lower_model.b
        self.nF = cached.shape[1]
        self.nP = getattr(lower_model, 'nP', 1)
        self.nO = cached.shape[2]
        self.ops = lower_model.ops
        self._is_synchronized = False
        self._cuda_stream = cuda_stream
        self._cached = cached
        self._bp_hiddens = bp_features

    cdef const float* get_feat_weights(self) except NULL:
        if not self._is_synchronized and self._cuda_stream is not None:
            self._cuda_stream.synchronize()
            self._is_synchronized = True
        return <float*>self._cached.data

    def __call__(self, X):
        return self.begin_update(X)[0]

    def begin_update(self, token_ids, drop=0.):
        cdef np.ndarray state_vector = numpy.zeros(
            (token_ids.shape[0], self.nO, self.nP), dtype='f')
        # This is tricky, but (assuming GPU available);
        # - Input to forward on CPU
        # - Output from forward on CPU
        # - Input to backward on GPU!
        # - Output from backward on GPU
        bp_hiddens = self._bp_hiddens

        feat_weights = self.get_feat_weights()
        cdef int[:, ::1] ids = token_ids
        sum_state_features(<float*>state_vector.data,
            feat_weights, &ids[0,0],
            token_ids.shape[0], self.nF, self.nO*self.nP)
        state_vector += self.bias
        state_vector, bp_nonlinearity = self._nonlinearity(state_vector)

        def backward(d_state_vector_ids, sgd=None):
            d_state_vector, token_ids = d_state_vector_ids
            d_state_vector = bp_nonlinearity(d_state_vector, sgd)
            # This will usually be on GPU
            if not isinstance(d_state_vector, self.ops.xp.ndarray):
                d_state_vector = self.ops.xp.array(d_state_vector)
            d_tokens = bp_hiddens((d_state_vector, token_ids), sgd)
            return d_tokens
        return state_vector, backward

    def _nonlinearity(self, state_vector):
        if self.nP == 1:
            state_vector = state_vector.reshape(state_vector.shape[:-1])
            mask = state_vector >= 0.
            state_vector *= mask
        else:
            state_vector, mask = self.ops.maxout(state_vector)

        def backprop_nonlinearity(d_best, sgd=None):
            # Fix nans (which can occur from unseen classes.)
            d_best[self.ops.xp.isnan(d_best)] = 0.
            if self.nP == 1:
                d_best *= mask
                d_best = d_best.reshape((d_best.shape + (1,)))
                return d_best
            else:
                return self.ops.backprop_maxout(d_best, mask, self.nP)
        return state_vector, backprop_nonlinearity
