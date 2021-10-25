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



def ParserStepModel(
    tokvecs: Floats2d,
    bp_tokvecs: Callable,
    upper: Model[Floats2d, Floats2d],
    dropout: float=0.1,
    unseen_classes: Optional[List[int]]=None
) -> Model[Ints2d, Floats2d]:
    # TODO: Keep working on replacing all of this with just 'chain'
    state2vec = precompute_hiddens(
        tokvecs,
        bp_tokvecs
    )
    class_mask = numpy.zeros((self.nO,), dtype='f')
    class_mask.fill(1)
    if unseen_classes is not None:
        for class_ in unseen_classes:
            class_mask[class_] = 0.

    return _ParserStepModel(
        "ParserStep",
        step_forward,
        init=None,
        dims={"nO": upper.get_dim("nO")},
        layers=[state2vec, upper],
        attrs={
            "tokvecs": tokvecs,
            "bp_tokvecs": bp_tokvecs,
            "dropout_rate": dropout,
            "class_mask": class_mask
        }
    )


class _ParserStepModel(Model):
    # TODO: Remove need for all this stuff, so we can normalize this
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


def step_forward(model: _ParserStepModel, token_ids, is_train):
    # TODO: Eventually we hopefully can get rid of all of this?
    # If we make the 'class_mask' thing its own layer, we can just
    # have chain() here, right?
    state2vec, upper = model.layers
    vector, get_d_tokvecs = state2vec(token_ids, is_train)
    mask = None
    vec2scores = ensure_same_device(model.ops, vec2scores)
    dropout_rate = model.attrs["dropout_rate"]
    if is_train and dropout_rate > 0:
        mask = model.ops.get_dropout_mask(vector.shape, dropout_rate)
        vector *= mask
    scores, get_d_vector = vec2scores(vector, is_train)
    # If the class is unseen, make sure its score is minimum
    class_mask = model.attrs["class_mask"]
    scores[:, class_mask == 0] = model.ops.xp.nanmin(scores)

    def backprop_parser_step(d_scores):
        # Zero vectors for unseen classes
        d_scores *= model._class_mask
        d_vector = get_d_vector(d_scores)
        if mask is not None:
            d_vector *= mask
        return get_d_tokvecs(d_vector)
    
    return scores, backprop_parser_step


def precompute_hiddens(lower_model, feat_weights: Floats3d, bp_hiddens: Callable) -> Model:
    return Model(
        "precompute_hiddens",
        init=None,
        forward=_precompute_forward,
        dims={
            "nO": feat_weights.shape[2],
            "nP": lower_model.get_dim("nP") if lower_model.has_dim("nP") else 1,
            "nF": cached.shape[1]
        },
        ops=lower_model.ops
    )


def _precomputed_forward(
    model: Model[Ints2d, Floats2d],
    token_ids: Ints2d,
    is_train: bool
) -> Tuple[Floats2d, Callable]:
    nO = model.get_dim("nO")
    nP = model.get_dim("nP")
    bp_hiddens = model.attrs["bp_hiddens"]
    feat_weights = model.attrs["feat_weights"]
    bias = model.attrs["bias"]
    hidden = model.ops.alloc2f(
        token_ids.shape[0],
        nO * nP
    ) 
    # TODO: This is probably wrong, right?
    model.ops.scatter_add(
        hidden,
        feat_weights,
        token_ids
    )
    statevec, mask = model.ops.maxout(hidden.reshape((-1, nO, nP)))

    def backward(d_statevec):
        return bp_hiddens(
            model.ops.backprop_maxout(d_statevec, mask, nP)
        )
        
    return statevec, backward
