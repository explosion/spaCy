# cython: infer_types=True, cdivision=True, boundscheck=False
from typing import Any, List, Optional, Tuple, TypeVar, cast

from libc.stdlib cimport calloc, free, realloc
from libc.string cimport memcpy, memset
from libcpp.vector cimport vector

import numpy

cimport numpy as np

from thinc.api import (
    Linear,
    Model,
    NumpyOps,
    chain,
    glorot_uniform_init,
    list2array,
    normal_init,
    uniform_init,
    zero_init,
)

from thinc.backends.cblas cimport CBlas, saxpy, sgemm

from thinc.types import Floats1d, Floats2d, Floats3d, Floats4d, Ints1d, Ints2d

from ..errors import Errors
from ..pipeline._parser_internals import _beam_utils
from ..pipeline._parser_internals.batch import GreedyBatch

from ..pipeline._parser_internals._parser_utils cimport arg_max
from ..pipeline._parser_internals.stateclass cimport StateC, StateClass
from ..pipeline._parser_internals.transition_system cimport (
    TransitionSystem,
    c_apply_actions,
    c_transition_batch,
)

from ..tokens.doc import Doc
from ..util import registry

State = Any  # TODO


@registry.layers("spacy.TransitionModel.v2")
def TransitionModel(
    *,
    tok2vec: Model[List[Doc], List[Floats2d]],
    beam_width: int = 1,
    beam_density: float = 0.0,
    state_tokens: int,
    hidden_width: int,
    maxout_pieces: int,
    nO: Optional[int] = None,
    unseen_classes=set(),
) -> Model[Tuple[List[Doc], TransitionSystem], List[Tuple[State, List[Floats2d]]]]:
    """Set up a transition-based parsing model, using a maxout hidden
    layer and a linear output layer.
    """
    t2v_width = tok2vec.get_dim("nO") if tok2vec.has_dim("nO") else None
    tok2vec_projected = chain(tok2vec, list2array(), Linear(hidden_width, t2v_width))  # type: ignore
    tok2vec_projected.set_dim("nO", hidden_width)

    # FIXME: we use `output` as a container for the output layer's
    # weights and biases. Thinc optimizers cannot handle resizing
    # of parameters. So, when the parser model is resized, we
    # construct a new `output` layer, which has a different key in
    # the optimizer. Once the optimizer supports parameter resizing,
    # we can replace the `output` layer by `output_W` and `output_b`
    # parameters in this model.
    output = Linear(nO=None, nI=hidden_width, init_W=zero_init)

    return Model(
        name="parser_model",
        forward=forward,
        init=init,
        layers=[tok2vec_projected, output],
        refs={
            "tok2vec": tok2vec_projected,
            "output": output,
        },
        params={
            "hidden_W": None,  # Floats2d W for the hidden layer
            "hidden_b": None,  # Floats1d bias for the hidden layer
            "hidden_pad": None,  # Floats1d padding for the hidden layer
        },
        dims={
            "nO": None,  # Output size
            "nP": maxout_pieces,
            "nH": hidden_width,
            "nI": tok2vec_projected.maybe_get_dim("nO"),
            "nF": state_tokens,
        },
        attrs={
            "beam_width": beam_width,
            "beam_density": beam_density,
            "unseen_classes": set(unseen_classes),
            "resize_output": resize_output,
        },
    )


def resize_output(model: Model, new_nO: int) -> Model:
    old_nO = model.maybe_get_dim("nO")
    output = model.get_ref("output")
    if old_nO is None:
        model.set_dim("nO", new_nO)
        output.set_dim("nO", new_nO)
        output.initialize()
        return model
    elif new_nO <= old_nO:
        return model
    elif output.has_param("W"):
        nH = model.get_dim("nH")
        new_output = Linear(nO=new_nO, nI=nH, init_W=zero_init)
        new_output.initialize()
        new_W = new_output.get_param("W")
        new_b = new_output.get_param("b")
        old_W = output.get_param("W")
        old_b = output.get_param("b")
        new_W[:old_nO] = old_W  # type: ignore
        new_b[:old_nO] = old_b  # type: ignore
        for i in range(old_nO, new_nO):
            model.attrs["unseen_classes"].add(i)
        model.layers[-1] = new_output
        model.set_ref("output", new_output)
    # TODO: Avoid this private intrusion
    model._dims["nO"] = new_nO
    return model


def init(
    model,
    X: Optional[Tuple[List[Doc], TransitionSystem]] = None,
    Y: Optional[Tuple[List[State], List[Floats2d]]] = None,
):
    if X is not None:
        docs, moves = X
        model.get_ref("tok2vec").initialize(X=docs)
    else:
        model.get_ref("tok2vec").initialize()
    inferred_nO = _infer_nO(Y)
    if inferred_nO is not None:
        current_nO = model.maybe_get_dim("nO")
        if current_nO is None or current_nO != inferred_nO:
            model.attrs["resize_output"](model, inferred_nO)
    nO = model.get_dim("nO")
    nP = model.get_dim("nP")
    nH = model.get_dim("nH")
    nI = model.get_dim("nI")
    nF = model.get_dim("nF")
    ops = model.ops

    Wl = ops.alloc2f(nH * nP, nF * nI)
    bl = ops.alloc1f(nH * nP)
    padl = ops.alloc1f(nI)
    # Wl = zero_init(ops, Wl.shape)
    Wl = glorot_uniform_init(ops, Wl.shape)
    padl = uniform_init(ops, padl.shape)  # type: ignore
    # TODO: Experiment with whether better to initialize output_W
    model.set_param("hidden_W", Wl)
    model.set_param("hidden_b", bl)
    model.set_param("hidden_pad", padl)
    # model = _lsuv_init(model)
    return model


class TransitionModelInputs:
    """
    Input to transition model.
    """

    # dataclass annotation is not yet supported in Cython 0.29.x,
    # so, we'll do something close to it.

    actions: Optional[List[Ints1d]]
    docs: List[Doc]
    max_moves: int
    moves: TransitionSystem
    states: Optional[List[State]]

    __slots__ = [
        "actions",
        "docs",
        "max_moves",
        "moves",
        "states",
    ]

    def __init__(
        self,
        docs: List[Doc],
        moves: TransitionSystem,
        actions: Optional[List[Ints1d]]=None,
        max_moves: int=0,
        states: Optional[List[State]]=None):
        """
        actions (Optional[List[Ints1d]]): actions to apply for each Doc.
        docs (List[Doc]): Docs to predict transition sequences for.
        max_moves: (int): the maximum number of moves to apply, values less
            than 1 will apply moves to states until they are final states.
        moves (TransitionSystem): the transition system to use when predicting
            the transition sequences.
        states (Optional[List[States]]): the initial states to predict the
            transition sequences for. When absent, the initial states are
            initialized from the provided Docs.
        """
        self.actions = actions
        self.docs = docs
        self.moves = moves
        self.max_moves = max_moves
        self.states = states


def forward(model, inputs: TransitionModelInputs, is_train: bool):
    docs = inputs.docs
    moves = inputs.moves
    actions = inputs.actions

    beam_width = model.attrs["beam_width"]
    hidden_pad = model.get_param("hidden_pad")
    tok2vec = model.get_ref("tok2vec")

    states = moves.init_batch(docs) if inputs.states is None else inputs.states
    tokvecs, backprop_tok2vec = tok2vec(docs, is_train)
    tokvecs = model.ops.xp.vstack((tokvecs, hidden_pad))
    feats, backprop_feats = _forward_precomputable_affine(model, tokvecs, is_train)
    seen_mask = _get_seen_mask(model)

    if not is_train and beam_width == 1 and isinstance(model.ops, NumpyOps):
        # Note: max_moves is only used during training, so we don't need to
        #       pass it to the greedy inference path.
        return _forward_greedy_cpu(model, moves, states, feats, seen_mask, actions=actions)
    else:
        return _forward_fallback(model, moves, states, tokvecs, backprop_tok2vec,
            feats, backprop_feats, seen_mask, is_train, actions=actions,
            max_moves=inputs.max_moves)


def _forward_greedy_cpu(model: Model, TransitionSystem moves, states: List[StateClass], np.ndarray feats,
                np.ndarray[np.npy_bool, ndim=1] seen_mask, actions: Optional[List[Ints1d]]=None):
    cdef vector[StateC*] c_states
    cdef StateClass state
    for state in states:
        if not state.is_final():
            c_states.push_back(state.c)
    weights = _get_c_weights(model, <float*>feats.data, seen_mask)
    # Precomputed features have rows for each token, plus one for padding.
    cdef int n_tokens = feats.shape[0] - 1
    sizes = _get_c_sizes(model, c_states.size(), n_tokens)
    cdef CBlas cblas = model.ops.cblas()
    scores = _parse_batch(cblas, moves, &c_states[0], weights, sizes, actions=actions)

    def backprop(dY):
        raise ValueError(Errors.E4004)

    return (states, scores), backprop

cdef list _parse_batch(CBlas cblas, TransitionSystem moves, StateC** states,
                       WeightsC weights, SizesC sizes, actions: Optional[List[Ints1d]]=None):
    cdef int i, j
    cdef vector[StateC *] unfinished
    cdef ActivationsC activations = _alloc_activations(sizes)
    cdef np.ndarray step_scores
    cdef np.ndarray step_actions

    scores = []
    while sizes.states >= 1 and (actions is None or len(actions) > 0):
        step_scores = numpy.empty((sizes.states, sizes.classes), dtype="f")
        step_actions = actions[0] if actions is not None else None
        assert step_actions is None or step_actions.size == sizes.states, \
            f"number of step actions ({step_actions.size}) must equal number of states ({sizes.states})"
        with nogil:
            _predict_states(cblas, &activations, <float*>step_scores.data, states, &weights, sizes)
            if actions is None:
                # Validate actions, argmax, take action.
                c_transition_batch(moves, states, <const float*>step_scores.data, sizes.classes,
                    sizes.states)
            else:
                c_apply_actions(moves, states, <const int*>step_actions.data, sizes.states)
            for i in range(sizes.states):
                if not states[i].is_final():
                    unfinished.push_back(states[i])
            for i in range(unfinished.size()):
                states[i] = unfinished[i]
        sizes.states = unfinished.size()
        scores.append(step_scores)
        unfinished.clear()
        actions = actions[1:] if actions is not None else None
    _free_activations(&activations)

    return scores


def _forward_fallback(
    model: Model,
    moves: TransitionSystem,
    states: List[StateClass],
    tokvecs, backprop_tok2vec,
    feats,
    backprop_feats,
    seen_mask,
    is_train: bool,
    actions: Optional[List[Ints1d]]=None,
    max_moves: int=0):
    nF = model.get_dim("nF")
    output = model.get_ref("output")
    hidden_b = model.get_param("hidden_b")
    nH = model.get_dim("nH")
    nP = model.get_dim("nP")

    beam_width = model.attrs["beam_width"]
    beam_density = model.attrs["beam_density"]

    ops = model.ops

    all_ids = []
    all_which = []
    all_statevecs = []
    all_scores = []
    if beam_width == 1:
        batch = GreedyBatch(moves, states, None)
    else:
        batch = _beam_utils.BeamBatch(
            moves, states, None, width=beam_width, density=beam_density
        )
    arange = ops.xp.arange(nF)
    n_moves = 0
    while not batch.is_done:
        ids = numpy.zeros((len(batch.get_unfinished_states()), nF), dtype="i")
        for i, state in enumerate(batch.get_unfinished_states()):
            state.set_context_tokens(ids, i, nF)
        # Sum the state features, add the bias and apply the activation (maxout)
        # to create the state vectors.
        preacts2f = feats[ids, arange].sum(axis=1)  # type: ignore
        preacts2f += hidden_b
        preacts = ops.reshape3f(preacts2f, preacts2f.shape[0], nH, nP)
        assert preacts.shape[0] == len(batch.get_unfinished_states()), preacts.shape
        statevecs, which = ops.maxout(preacts)
        # We don't use output's backprop, since we want to backprop for
        # all states at once, rather than a single state.
        scores = output.predict(statevecs)
        scores[:, seen_mask] = ops.xp.nanmin(scores)
        # Transition the states, filtering out any that are finished.
        cpu_scores = ops.to_numpy(scores)
        if actions is None:
            batch.advance(cpu_scores)
        else:
            batch.advance_with_actions(actions[0])
            actions = actions[1:]
        all_scores.append(scores)
        if is_train:
            # Remember intermediate results for the backprop.
            all_ids.append(ids)
            all_statevecs.append(statevecs)
            all_which.append(which)
        if n_moves >= max_moves >= 1:
            break
        n_moves += 1

    def backprop_parser(d_states_d_scores):
        ids = ops.xp.vstack(all_ids)
        which = ops.xp.vstack(all_which)
        statevecs = ops.xp.vstack(all_statevecs)
        _, d_scores = d_states_d_scores
        if model.attrs.get("unseen_classes"):
            # If we have a negative gradient (i.e. the probability should
            # increase) on any classes we filtered out as unseen, mark
            # them as seen.
            for clas in set(model.attrs["unseen_classes"]):
                if (d_scores[:, clas] < 0).any():
                    model.attrs["unseen_classes"].remove(clas)
        d_scores *= seen_mask == False
        # Calculate the gradients for the parameters of the output layer.
        # The weight gemm is (nS, nO) @ (nS, nH).T
        output.inc_grad("b", d_scores.sum(axis=0))
        output.inc_grad("W", ops.gemm(d_scores, statevecs, trans1=True))
        # Now calculate d_statevecs, by backproping through the output linear layer.
        # This gemm is (nS, nO) @ (nO, nH)
        output_W = output.get_param("W")
        d_statevecs = ops.gemm(d_scores, output_W)
        # Backprop through the maxout activation
        d_preacts = ops.backprop_maxout(d_statevecs, which, nP)
        d_preacts2f = ops.reshape2f(d_preacts, d_preacts.shape[0], nH * nP)
        model.inc_grad("hidden_b", d_preacts2f.sum(axis=0))
        # We don't need to backprop the summation, because we pass back the IDs instead
        d_state_features = backprop_feats((d_preacts2f, ids))
        d_tokvecs = ops.alloc2f(tokvecs.shape[0], tokvecs.shape[1])
        ops.scatter_add(d_tokvecs, ids, d_state_features)
        model.inc_grad("hidden_pad", d_tokvecs[-1])
        return (backprop_tok2vec(d_tokvecs[:-1]), None)

    return (list(batch), all_scores), backprop_parser


def _get_seen_mask(model: Model) -> numpy.array[bool, 1]:
    mask = model.ops.xp.zeros(model.get_dim("nO"), dtype="bool")
    for class_ in model.attrs.get("unseen_classes", set()):
        mask[class_] = True
    return mask


def _forward_precomputable_affine(model, X: Floats2d, is_train: bool):
    W: Floats2d = model.get_param("hidden_W")
    nF = model.get_dim("nF")
    nH = model.get_dim("nH")
    nP = model.get_dim("nP")
    nI = model.get_dim("nI")
    # The weights start out (nH * nP, nF * nI). Transpose and reshape to (nF * nH *nP, nI)
    W3f = model.ops.reshape3f(W, nH * nP, nF, nI)
    W3f = W3f.transpose((1, 0, 2))
    W2f = model.ops.reshape2f(W3f, nF * nH * nP, nI)
    assert X.shape == (X.shape[0], nI), X.shape
    Yf_ = model.ops.gemm(X, W2f, trans2=True)
    Yf = model.ops.reshape3f(Yf_, Yf_.shape[0], nF, nH * nP)

    def backward(dY_ids: Tuple[Floats3d, Ints2d]):
        # This backprop is particularly tricky, because we get back a different
        # thing from what we put out. We put out an array of shape:
        # (nB, nF, nH, nP), and get back:
        # (nB, nH, nP) and ids (nB, nF)
        # The ids tell us the values of nF, so we would have:
        #
        # dYf = zeros((nB, nF, nH, nP))
        # for b in range(nB):
        #     for f in range(nF):
        #         dYf[b, ids[b, f]] += dY[b]
        #
        # However, we avoid building that array for efficiency -- and just pass
        # in the indices.
        dY, ids = dY_ids
        dXf = model.ops.gemm(dY, W)
        Xf = X[ids].reshape((ids.shape[0], -1))
        dW = model.ops.gemm(dY, Xf, trans1=True)
        model.inc_grad("hidden_W", dW)
        return model.ops.reshape3f(dXf, dXf.shape[0], nF, nI)

    return Yf, backward


def _infer_nO(Y: Optional[Tuple[List[State], List[Floats2d]]]) -> Optional[int]:
    if Y is None:
        return None
    _, scores = Y
    if len(scores) == 0:
        return None
    assert scores[0].shape[0] >= 1
    assert len(scores[0].shape) == 2
    return scores[0].shape[1]


def _lsuv_init(model: Model):
    """This is like the 'layer sequential unit variance', but instead
    of taking the actual inputs, we randomly generate whitened data.

    Why's this all so complicated? We have a huge number of inputs,
    and the maxout unit makes guessing the dynamics tricky. Instead
    we set the maxout weights to values that empirically result in
    whitened outputs given whitened inputs.
    """
    W = model.maybe_get_param("hidden_W")
    if W is not None and W.any():
        return

    nF = model.get_dim("nF")
    nH = model.get_dim("nH")
    nP = model.get_dim("nP")
    nI = model.get_dim("nI")
    W = model.ops.alloc4f(nF, nH, nP, nI)
    b = model.ops.alloc2f(nH, nP)
    pad = model.ops.alloc4f(1, nF, nH, nP)

    ops = model.ops
    W = normal_init(ops, W.shape, mean=float(ops.xp.sqrt(1.0 / nF * nI)))
    pad = normal_init(ops, pad.shape, mean=1.0)
    model.set_param("W", W)
    model.set_param("b", b)
    model.set_param("pad", pad)

    ids = ops.alloc_f((5000, nF), dtype="f")
    ids += ops.xp.random.uniform(0, 1000, ids.shape)
    ids = ops.asarray(ids, dtype="i")
    tokvecs = ops.alloc_f((5000, nI), dtype="f")
    tokvecs += ops.xp.random.normal(loc=0.0, scale=1.0, size=tokvecs.size).reshape(
        tokvecs.shape
    )

    def predict(ids, tokvecs):
        # nS ids. nW tokvecs. Exclude the padding array.
        hiddens, _ = _forward_precomputable_affine(model, tokvecs[:-1], False)
        vectors = model.ops.alloc2f(ids.shape[0], nH * nP)
        # need nS vectors
        hiddens = hiddens.reshape((hiddens.shape[0] * nF, nH * nP))
        model.ops.scatter_add(vectors, ids.flatten(), hiddens)
        vectors3f = model.ops.reshape3f(vectors, vectors.shape[0], nH, nP)
        vectors3f += b
        return model.ops.maxout(vectors3f)[0]

    tol_var = 0.01
    tol_mean = 0.01
    t_max = 10
    W = cast(Floats4d, model.get_param("hidden_W").copy())
    b = cast(Floats2d, model.get_param("hidden_b").copy())
    for t_i in range(t_max):
        acts1 = predict(ids, tokvecs)
        var = model.ops.xp.var(acts1)
        mean = model.ops.xp.mean(acts1)
        if abs(var - 1.0) >= tol_var:
            W /= model.ops.xp.sqrt(var)
            model.set_param("hidden_W", W)
        elif abs(mean) >= tol_mean:
            b -= mean
            model.set_param("hidden_b", b)
        else:
            break
    return model


cdef WeightsC _get_c_weights(model, const float* feats, np.ndarray[np.npy_bool, ndim=1] seen_mask) except *:
    output = model.get_ref("output")
    cdef np.ndarray hidden_b = model.get_param("hidden_b")
    cdef np.ndarray output_W = output.get_param("W")
    cdef np.ndarray output_b = output.get_param("b")

    cdef WeightsC weights
    weights.feat_weights = feats
    weights.feat_bias = <const float*>hidden_b.data
    weights.hidden_weights = <const float *> output_W.data
    weights.hidden_bias = <const float *> output_b.data
    weights.seen_mask = <const int8_t*> seen_mask.data

    return weights


cdef SizesC _get_c_sizes(model, int batch_size, int tokens) except *:
    cdef SizesC sizes
    sizes.states = batch_size
    sizes.classes = model.get_dim("nO")
    sizes.hiddens = model.get_dim("nH")
    sizes.pieces = model.get_dim("nP")
    sizes.feats = model.get_dim("nF")
    sizes.embed_width = model.get_dim("nI")
    sizes.tokens = tokens
    return sizes


cdef ActivationsC _alloc_activations(SizesC n) nogil:
    cdef ActivationsC A
    memset(&A, 0, sizeof(A))
    _resize_activations(&A, n)
    return A


cdef void _free_activations(const ActivationsC* A) nogil:
    free(A.token_ids)
    free(A.unmaxed)
    free(A.hiddens)
    free(A.is_valid)


cdef void _resize_activations(ActivationsC* A, SizesC n) nogil:
    if n.states <= A._max_size:
        A._curr_size = n.states
        return
    if A._max_size == 0:
        A.token_ids = <int*>calloc(n.states * n.feats, sizeof(A.token_ids[0]))
        A.unmaxed = <float*>calloc(n.states * n.hiddens * n.pieces, sizeof(A.unmaxed[0]))
        A.hiddens = <float*>calloc(n.states * n.hiddens, sizeof(A.hiddens[0]))
        A.is_valid = <int*>calloc(n.states * n.classes, sizeof(A.is_valid[0]))
        A._max_size = n.states
    else:
        A.token_ids = <int*>realloc(A.token_ids,
            n.states * n.feats * sizeof(A.token_ids[0]))
        A.unmaxed = <float*>realloc(A.unmaxed,
            n.states * n.hiddens * n.pieces * sizeof(A.unmaxed[0]))
        A.hiddens = <float*>realloc(A.hiddens,
            n.states * n.hiddens * sizeof(A.hiddens[0]))
        A.is_valid = <int*>realloc(A.is_valid,
            n.states * n.classes * sizeof(A.is_valid[0]))
        A._max_size = n.states
    A._curr_size = n.states


cdef void _predict_states(CBlas cblas, ActivationsC* A, float* scores, StateC** states, const WeightsC* W, SizesC n) nogil:
    _resize_activations(A, n)
    for i in range(n.states):
        states[i].set_context_tokens(&A.token_ids[i*n.feats], n.feats)
    memset(A.unmaxed, 0, n.states * n.hiddens * n.pieces * sizeof(float))
    _sum_state_features(cblas, A.unmaxed, W.feat_weights, A.token_ids, n)
    for i in range(n.states):
        saxpy(cblas)(n.hiddens * n.pieces, 1., W.feat_bias, 1, &A.unmaxed[i*n.hiddens*n.pieces], 1)
        for j in range(n.hiddens):
            index = i * n.hiddens * n.pieces + j * n.pieces
            which = arg_max(&A.unmaxed[index], n.pieces)
            A.hiddens[i*n.hiddens + j] = A.unmaxed[index + which]
    if W.hidden_weights == NULL:
        memcpy(scores, A.hiddens, n.states * n.classes * sizeof(float))
    else:
        # Compute hidden-to-output
        sgemm(cblas)(False, True, n.states, n.classes, n.hiddens,
                      1.0, <const float *>A.hiddens, n.hiddens,
                      <const float *>W.hidden_weights, n.hiddens,
                      0.0, scores, n.classes)
        # Add bias
        for i in range(n.states):
            saxpy(cblas)(n.classes, 1., W.hidden_bias, 1, &scores[i*n.classes], 1)
    # Set unseen classes to minimum value
    i = 0
    min_ = scores[0]
    for i in range(1, n.states * n.classes):
        if scores[i] < min_:
            min_ = scores[i]
    for i in range(n.states):
        for j in range(n.classes):
            if W.seen_mask[j]:
                scores[i*n.classes+j] = min_


cdef void _sum_state_features(CBlas cblas, float* output,
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
            saxpy(cblas)(O, one, <const float*>feature, 1, &output[b*O], 1)
        token_ids += F

