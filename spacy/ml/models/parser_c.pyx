# cython: infer_types=True, cdivision=True, boundscheck=False
cimport numpy as np
from libc.string cimport memset, memcpy
from libc.stdlib cimport calloc, free, realloc
from libcpp.vector cimport vector
from thinc.backends.linalg cimport Vec, VecVec
cimport blis.cy

from thinc.api import Model

from spacy.pipeline._parser_internals.transition_system cimport c_transition_batch, TransitionSystem
from spacy.pipeline._parser_internals.stateclass cimport StateClass


cpdef forward_cpu(model: Model, TransitionSystem moves, states: List[StateClass], np.ndarray feats,
                  np.ndarray[np.npy_bool, ndim=1] seen_mask):
    cdef vector[StateC*] c_states
    cdef StateClass state
    for state in states:
        if not state.is_final():
            c_states.push_back(state.c)
    cdef object featsp = feats
    weights = get_c_weights(model, <float*>feats.data, seen_mask)
    # Precomputed features have rows for each token, plus one for padding.
    cdef int n_tokens = feats.shape[0] - 1
    sizes = get_c_sizes(model, c_states.size(), n_tokens)
    with nogil:
        _parseC(moves, &c_states[0], weights, sizes)

    # TODO: scores
    return states, []

cdef void _parseC(TransitionSystem moves, StateC** states,
                  WeightsC weights, SizesC sizes) nogil:
    cdef int i, j
    cdef vector[StateC *] unfinished
    cdef ActivationsC activations = alloc_activations(sizes)
    while sizes.states >= 1:
        predict_states(&activations, states, &weights, sizes)
        # Validate actions, argmax, take action.
        c_transition_batch(moves, states, activations.scores, sizes.classes,
           sizes.states)
        for i in range(sizes.states):
            if not states[i].is_final():
                unfinished.push_back(states[i])
        for i in range(unfinished.size()):
            states[i] = unfinished[i]
        sizes.states = unfinished.size()
        unfinished.clear()
    free_activations(&activations)


cdef WeightsC get_c_weights(model, const float* feats, np.ndarray[np.npy_bool, ndim=1] seen_mask) except *:
    cdef np.ndarray lower_bias = model.get_param("lower_b")
    cdef np.ndarray upper_W = model.get_param("upper_W")
    cdef np.ndarray upper_b = model.get_param("upper_b")

    cdef WeightsC output
    output.feat_weights = feats
    output.feat_bias = <const float*>lower_bias.data
    output.hidden_weights = <const float *> upper_W.data
    output.hidden_bias = <const float *> upper_b.data
    output.seen_mask = <const int8_t*> seen_mask.data

    return output


cdef SizesC get_c_sizes(model, int batch_size, int tokens) except *:
    cdef SizesC output
    output.states = batch_size
    output.classes = model.get_dim("nO")
    output.hiddens = model.get_dim("nH")
    output.pieces = model.get_dim("nP")
    output.feats = model.get_dim("nF")
    output.embed_width = model.get_dim("nI")
    output.tokens = tokens
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


cdef void predict_states(ActivationsC* A, StateC** states, const WeightsC* W, SizesC n) nogil:
    cdef double one = 1.0
    resize_activations(A, n)
    for i in range(n.states):
        states[i].set_context_tokens(&A.token_ids[i*n.feats], n.feats)
    memset(A.unmaxed, 0, n.states * n.hiddens * n.pieces * sizeof(float))
    sum_state_features(A.unmaxed, W.feat_weights, A.token_ids, n)
    for i in range(n.states):
        VecVec.add_i(&A.unmaxed[i*n.hiddens*n.pieces],
            W.feat_bias, 1., n.hiddens * n.pieces)
        for j in range(n.hiddens):
            index = i * n.hiddens * n.pieces + j * n.pieces
            which = Vec.arg_max(&A.unmaxed[index], n.pieces)
            A.hiddens[i*n.hiddens + j] = A.unmaxed[index + which]
    if W.hidden_weights == NULL:
        memcpy(A.scores, A.hiddens, n.states * n.classes * sizeof(float))
    else:
        # Compute hidden-to-output
        blis.cy.gemm(blis.cy.NO_TRANSPOSE, blis.cy.TRANSPOSE,
            n.states, n.classes, n.hiddens, one,
            <float*>A.hiddens, n.hiddens, 1,
            <float*>W.hidden_weights, n.hiddens, 1,
            0.0,
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
            if W.seen_mask[j]:
                A.scores[i*n.classes+j] = min_


cdef void sum_state_features(float* output,
        const float* cached, const int* token_ids, SizesC n) nogil:
    cdef int idx, b, f, i
    cdef const float* feature
    cdef int B = n.states
    cdef int O = n.hiddens * n.pieces
    cdef int F = n.feats
    cdef int T = n.tokens
    padding = cached + (T * F * O)
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
