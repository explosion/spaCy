# cython: infer_types=True, cdivision=True, boundscheck=False
cimport numpy as np
from libc.math cimport exp
from libc.string cimport memset, memcpy
from libc.stdlib cimport calloc, free, realloc
from thinc.backends.linalg cimport Vec, VecVec
cimport blis.cy

import numpy
import numpy.random
from thinc.api import Model, CupyOps, NumpyOps

from .. import util
from ..typedefs cimport weight_t, class_t, hash_t
from ..pipeline._parser_internals.stateclass cimport StateClass


cdef WeightsC get_c_weights(model) except *:
    cdef WeightsC output
    cdef precompute_hiddens state2vec = model.state2vec
    cdef np.ndarray bias = state2vec.bias
    output.feat_weights = state2vec.get_feat_weights()
    output.feat_bias = <const float*>bias.data
    cdef np.ndarray vec2scores_W
    cdef np.ndarray vec2scores_b
    if model.vec2scores is None:
        output.hidden_weights = NULL
        output.hidden_bias = NULL
    else:
        vec2scores_W = model.vec2scores.get_param("W")
        vec2scores_b = model.vec2scores.get_param("b")
        output.hidden_weights = <const float*>vec2scores_W.data
        output.hidden_bias = <const float*>vec2scores_b.data
    cdef np.ndarray class_mask = model._class_mask
    output.seen_classes = <const float*>class_mask.data
    return output


cdef SizesC get_c_sizes(model, int batch_size) except *:
    cdef SizesC output
    output.states = batch_size
    if model.vec2scores is None:
        output.classes = model.state2vec.get_dim("nO")
    else:
        output.classes = model.vec2scores.get_dim("nO")
    output.hiddens = model.state2vec.get_dim("nO")
    output.pieces = model.state2vec.get_dim("nP")
    output.feats = model.state2vec.get_dim("nF")
    output.embed_width = model.tokvecs.shape[1]
    return output


cdef ActivationsC alloc_activations(SizesC n) nogil:
    cdef ActivationsC A
    memset(&A, 0, sizeof(A))
    resize_activations(&A, n)
    return A


cdef void free_activations(const ActivationsC* A) nogil:
    free(A.token_ids)
    free(A.scores)
    free(A.unmaxed)
    free(A.hiddens)
    free(A.is_valid)


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
    cdef double one = 1.0
    resize_activations(A, n)
    for i in range(n.states):
        states[i].set_context_tokens(&A.token_ids[i*n.feats], n.feats)
    memset(A.unmaxed, 0, n.states * n.hiddens * n.pieces * sizeof(float))
    memset(A.hiddens, 0, n.states * n.hiddens * sizeof(float))
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
    if W.hidden_weights == NULL:
        memcpy(A.scores, A.hiddens, n.states * n.classes * sizeof(float))
    else:
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



class ParserStepModel(Model):
    def __init__(self, docs, layers, *, has_upper, unseen_classes=None, train=True,
            dropout=0.1):
        Model.__init__(self, name="parser_step_model", forward=step_forward)
        self.attrs["has_upper"] = has_upper
        self.attrs["dropout_rate"] = dropout
        self.tokvecs, self.bp_tokvecs = layers[0](docs, is_train=train)
        if layers[1].get_dim("nP") >= 2:
            activation = "maxout"
        elif has_upper:
            activation = None
        else:
            activation = "relu"
        self.state2vec = precompute_hiddens(
            len(docs),
            self.tokvecs,
            layers[1],
            activation=activation,
            train=train
        )
        if has_upper:
            self.vec2scores = layers[-1]
        else:
            self.vec2scores = None
        self._class_mask = numpy.zeros((self.nO,), dtype='f')
        self._class_mask.fill(1)
        if unseen_classes is not None:
            for class_ in unseen_classes:
                self._class_mask[class_] = 0.

    @property
    def nO(self):
        if self.attrs["has_upper"]:
            return self.vec2scores.get_dim("nO")
        else:
            return self.state2vec.get_dim("nO")

    def clear_memory(self):
        del self.tokvecs
        del self.bp_tokvecs
        del self.state2vec
        del self.backprops
        del self._class_mask

    def class_is_unseen(self, class_):
        return self._class_mask[class_]

    def mark_class_unseen(self, class_):
        self._class_mask[class_] = 0

    def mark_class_seen(self, class_):
        self._class_mask[class_] = 1

    def get_token_ids(self, states):
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


def step_forward(model: ParserStepModel, token_ids, is_train):
    vector, get_d_tokvecs = model.state2vec(token_ids, is_train)
    mask = None
    if model.attrs["has_upper"]:
        vec2scores = ensure_same_device(model.ops, model.vec2scores)
        dropout_rate = model.attrs["dropout_rate"]
        if is_train and dropout_rate > 0:
            mask = model.ops.get_dropout_mask(vector.shape, dropout_rate)
            vector *= mask
        scores, get_d_vector = vec2scores(vector, is_train)
    else:
        scores = vector
        get_d_vector = lambda d_scores: d_scores
    # If the class is unseen, make sure its score is minimum
    scores[:, model._class_mask == 0] = model.ops.xp.nanmin(scores)

    def backprop_parser_step(d_scores):
        # Zero vectors for unseen classes
        d_scores *= model._class_mask
        d_vector = get_d_vector(d_scores)
        if mask is not None:
            d_vector *= mask
        return get_d_tokvecs(d_vector)
    
    return scores, backprop_parser_step


def ensure_same_device(ops, model):
    """Ensure a model is on the same device as a given ops"""
    if not isinstance(model.ops, ops.__class__):
        model._to_ops(ops)
    return model


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
    cdef public object ops
    cdef readonly object bias
    cdef readonly object activation
    cdef readonly object _features
    cdef readonly object _cached
    cdef readonly object _bp_hiddens

    def __init__(
        self,
        batch_size,
        tokvecs,
        lower_model, 
        activation="maxout",
        train=False
    ):
        cached, bp_features = lower_model(tokvecs, train)
        self.bias = lower_model.get_param("b")
        self.nF = cached.shape[1]
        if lower_model.has_dim("nP"):
            self.nP = lower_model.get_dim("nP")
        else:
            self.nP = 1
        self.nO = cached.shape[2]
        self.ops = lower_model.ops
        assert activation in (None, "relu", "maxout")
        self.activation = activation
        self._cached = cached
        self._bp_hiddens = bp_features

    cdef const float* get_feat_weights(self) except NULL:
        cdef np.ndarray cached
        if isinstance(self._cached, numpy.ndarray):
            cached = self._cached
        else:
            cached = self._cached.get()
        return <float*>cached.data

    def has_dim(self, name):
        if name == "nF":
            return self.nF if self.nF is not None else True
        elif name == "nP":
            return self.nP if self.nP is not None else True
        elif name == "nO":
            return self.nO if self.nO is not None else True
        else:
            return False

    def get_dim(self, name):
        if name == "nF":
            return self.nF
        elif name == "nP":
            return self.nP
        elif name == "nO":
            return self.nO
        else:
            raise ValueError(f"Dimension {name} invalid -- only nO, nF, nP")

    def set_dim(self, name, value):
        if name == "nF":
            self.nF = value
        elif name == "nP":
            self.nP = value
        elif name == "nO":
            self.nO = value
        else:
            raise ValueError(f"Dimension {name} invalid -- only nO, nF, nP")

    def __call__(self, X, bint is_train):
        if is_train:
            return self.begin_update(X)
        else:
            return self.predict(X), lambda X: X

    def predict(self, X):
        return self.begin_update(X)[0]

    def begin_update(self, token_ids):
        nO = self.nO
        nP = self.nP
        hidden = self.model.ops.alloc2f(
            token_ids.shape[0],
            nO * nP
        ) 
        bp_hiddens = self._bp_hiddens
        feat_weights = self.cached
        self.ops.scatter_add(
            hidden,
            feat_weights,
            token_ids
        )
        hidden += self.bias
        statevec, mask = self.ops.maxout(hidden.reshape((-1, nO, nP)))

        def backward(d_statevec):
            return bp_hiddens(
                self.ops.backprop_maxout(d_statevec, mask, nP)
            )
        
        return statevec, backward
