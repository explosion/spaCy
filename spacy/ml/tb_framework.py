from typing import List, Tuple, Any, Optional
from thinc.api import Ops, Model, normal_init
from thinc.types import Floats1d, Floats2d, Floats3d, Ints2d, Floats4d
from ..tokens.doc import Doc


TransitionSystem = Any  # TODO
State = Any  # TODO


def TransitionModel(
    *,
    tok2vec: Model[List[Doc], List[Floats2d]],
    state_tokens: int,
    hidden_width: int,
    maxout_pieces: int,
    nO: Optional[int] = None,
    unseen_classes=set(),
) -> Model[Tuple[List[Doc], TransitionSystem], List[Tuple[State, List[Floats2d]]]]:
    """Set up a transition-based parsing model, using a maxout hidden
    layer and a linear output layer.
    """
    return Model(
        name="parser_model",
        forward=forward,
        init=init,
        layers=[tok2vec],
        refs={"tok2vec": tok2vec},
        params={
            "lower_W": None,  # Floats2d W for the hidden layer
            "lower_b": None,  # Floats1d bias for the hidden layer
            "lower_pad": None,  # Floats1d bias for the hidden layer
            "upper_W": None,  # Floats2d W for the output layer
            "upper_b": None,  # Floats1d bias for the output layer
        },
        dims={
            "nO": None,  # Output size
            "nP": maxout_pieces,
            "nH": hidden_width,
            "nI": tok2vec.maybe_get_dim("nO"),
            "nF": state_tokens,
        },
        attrs={
            "unseen_classes": set(unseen_classes),
            "resize_output": resize_output,
            "make_step_model": make_step_model,
        },
    )


def make_step_model(model: Model) -> Model[List[State], Floats2d]:
    ...


def resize_output(model: Model) -> Model:
    ...


def init(
    model,
    X: Optional[Tuple[List[Doc], TransitionSystem]] = None,
    Y: Optional[Tuple[List[State], List[Floats2d]]] = None,
):
    if X is not None:
        docs, states = X
        model.get_ref("tok2vec").initialize(X=docs)
    inferred_nO = _infer_nO(Y)
    if inferred_nO is not None:
        current_nO = model.maybe_get_dim("nO")
        if current_nO is None:
            model.set_dim("nO", inferred_nO)
        elif current_nO != inferred_nO:
            model.attrs["resize_output"](model, inferred_nO)
    nO = model.get_dim("nO")
    nP = model.get_dim("nP")
    nH = model.get_dim("nH")
    nI = model.get_dim("nI")
    nF = model.get_dim("nF")
    ops = model.ops

    Wl = ops.alloc4f(nF, nH, nP, nI)
    bl = ops.alloc2f(nH, nP)
    padl = ops.alloc4f(1, nF, nH, nP)
    Wu = ops.alloc2f(nO, nH)
    bu = ops.alloc1f(nO)
    Wl = normal_init(ops, Wl.shape, mean=float(ops.xp.sqrt(1.0 / nF * nI)))
    padl = normal_init(ops, padl.shape, mean=1.0)
    # TODO: Experiment with whether better to initialize Wu
    model.set_param("lower_W", Wl)
    model.set_param("lower_b", bl)
    model.set_param("lower_pad", padl)
    model.set_param("upper_W", Wu)
    model.set_param("upper_b", bu)

    _lsuv_init(model)


def forward(model, docs_moves, is_train):
    tok2vec = model.get_ref("tok2vec")
    state2scores = model.get_ref("state2scores")
    # Get a reference to the parameters. We need to work with
    # stable references through the forward/backward pass, to make
    # sure we don't have a stale reference if there's concurrent shenanigans.
    params = {name: model.get_param(name) for name in model.param_names}
    ops = model.ops
    docs, moves = docs_moves
    states = moves.init_batch(docs)
    tokvecs, backprop_tok2vec = tok2vec(docs, is_train)
    feats, backprop_feats = _forward_precomputable_affine(model, tokvecs, is_train)
    memory = []
    all_scores = []
    while states:
        states, scores, memory = _step_parser(
            ops, params, moves, states, feats, memory, is_train
        )
        all_scores.append(scores)

    def backprop_parser(d_states_d_scores):
        _, d_scores = d_states_d_scores
        d_feats, ids = _backprop_parser_steps(ops, params, memory, d_scores)
        d_tokvecs = backprop_feats((d_feats, ids))
        return backprop_tok2vec(d_tokvecs), None

    return (states, all_scores), backprop_parser


def _step_parser(ops, params, moves, states, feats, memory, is_train):
    ids = moves.get_state_ids(states)
    statevecs, which, scores = _score_ids(ops, params, ids, feats, is_train)
    next_states = moves.transition_states(states, scores)
    if is_train:
        memory.append((ids, statevecs, which))
    return next_states, scores, memory


def _score_ids(ops, params, ids, feats, is_train):
    lower_pad = params["lower_pad"]
    lower_b = params["lower_b"]
    upper_W = params["upper_W"]
    upper_b = params["upper_b"]
    # During each step of the parser, we do:
    # * Index into the features, to get the pre-activated vector
    # for each (token, feature) and sum the feature vectors
    preacts = _sum_state_features(feats, lower_pad, ids)
    # * Add the bias
    preacts += lower_b
    # * Apply the activation (maxout)
    statevecs, which = ops.maxout(preacts)
    # * Multiply the state-vector by the scores weights
    scores = ops.gemm(statevecs, upper_W, trans2=True)
    # * Add the bias
    scores += upper_b
    # * Apply the is-class-unseen masking
    # TODO
    return statevecs, which, scores


def _sum_state_features(ops: Ops, feats: Floats3d, ids: Ints2d) -> Floats2d:
    # Here's what we're trying to implement here:
    #
    # for i in range(ids.shape[0]):
    #     for j in range(ids.shape[1]):
    #         output[i] += feats[ids[i, j], j]
    #
    # Reshape the feats into 2d, to make indexing easier. Instead of getting an
    # array of indices where the cell at (4, 2) needs to refer to the row at
    # feats[4, 2], we'll translate the index so that it directly addresses
    # feats[18]. This lets us make the indices array 1d, leading to fewer
    # numpy shennanigans.
    feats2d = ops.reshape2f(feats, feats.shape[0] * feats.shape[1], feats.shape[2])
    # Now translate the ids. If we're looking for the row that used to be at
    # (4, 1) and we have 4 features, we'll find it at (4*4)+1=17.
    oob_ids = ids < 0  # Retain the -1 values
    ids = ids * feats.shape[1] + ops.xp.arange(feats.shape[1])
    ids[oob_ids] = -1
    unsummed2d = feats2d[ops.reshape1i(ids, ids.size)]
    unsummed3d = ops.reshape3f(
        unsummed2d, feats.shape[0], feats.shape[1], feats.shape[2]
    )
    summed = unsummed3d.sum(axis=1)  # type: ignore
    return summed


def _process_memory(ops, memory):
    """Concatenate the memory buffers from each state into contiguous
    buffers for the whole batch.
    """
    return [ops.xp.concatenate(*item) for item in zip(*memory)]


def _backprop_parser_steps(model, upper_W, memory, d_scores):
    # During each step of the parser, we do:
    # * Index into the features, to get the pre-activated vector
    # for each (token, feature)
    # * Sum the feature vectors
    # * Add the bias
    # * Apply the activation (maxout)
    # * Multiply the state-vector by the scores weights
    # * Add the bias
    # * Apply the is-class-unseen masking
    #
    # So we have to backprop through all those steps.
    ids, statevecs, whiches = _process_memory(model.ops, memory)
    # TODO: Unseen class masking
    # Calculate the gradients for the parameters of the upper layer.
    model.inc_grad("upper_b", d_scores.sum(axis=0))
    model.inc_grad("upper_W", model.ops.gemm(d_scores, statevecs, trans1=True))
    # Now calculate d_statevecs, by backproping through the upper linear layer.
    d_statevecs = model.ops.gemm(d_scores, upper_W)
    # Backprop through the maxout activation
    d_preacts = model.ops.backprop_maxount(d_statevecs, whiches, model.get_dim("nP"))
    # We don't need to backprop the summation, because we pass back the IDs instead
    return d_preacts, ids


def _forward_precomputable_affine(model, X: Floats2d, is_train: bool):

    W: Floats4d = model.get_param("lower_W")
    b: Floats2d = model.get_param("lower_b")
    pad: Floats4d = model.get_param("lower_pad")
    nF = model.get_dim("nF")
    nO = model.get_dim("nO")
    nP = model.get_dim("nP")
    nI = model.get_dim("nI")
    Yf_ = model.ops.gemm(X, model.ops.reshape2f(W, nF * nO * nP, nI), trans2=True)
    Yf = model.ops.reshape4f(Yf_, Yf_.shape[0], nF, nO, nP)
    Yf = model.ops.xp.vstack((Yf, pad))

    def backward(dY_ids: Tuple[Floats3d, Ints2d]):
        # This backprop is particularly tricky, because we get back a different
        # thing from what we put out. We put out an array of shape:
        # (nB, nF, nO, nP), and get back:
        # (nB, nO, nP) and ids (nB, nF)
        # The ids tell us the values of nF, so we would have:
        #
        # dYf = zeros((nB, nF, nO, nP))
        # for b in range(nB):
        #     for f in range(nF):
        #         dYf[b, ids[b, f]] += dY[b]
        #
        # However, we avoid building that array for efficiency -- and just pass
        # in the indices.
        dY, ids = dY_ids
        assert dY.ndim == 3
        assert dY.shape[1] == nO, dY.shape
        assert dY.shape[2] == nP, dY.shape
        # nB = dY.shape[0]
        model.inc_grad(
            "lower_pad", _backprop_precomputable_affine_padding(model, dY, ids)
        )
        Xf = model.ops.reshape2f(X[ids], ids.shape[0], nF * nI)

        model.inc_grad("lower_b", dY.sum(axis=0))  # type: ignore
        dY = model.ops.reshape2f(dY, dY.shape[0], nO * nP)

        Wopfi = W.transpose((1, 2, 0, 3))
        Wopfi = Wopfi.reshape((nO * nP, nF * nI))
        dXf = model.ops.gemm(dY.reshape((dY.shape[0], nO * nP)), Wopfi)

        dWopfi = model.ops.gemm(dY, Xf, trans1=True)
        dWopfi = dWopfi.reshape((nO, nP, nF, nI))
        # (o, p, f, i) --> (f, o, p, i)
        dWopfi = dWopfi.transpose((2, 0, 1, 3))
        model.inc_grad("W", dWopfi)
        return model.ops.reshape3f(dXf, dXf.shape[0], nF, nI)

    return Yf, backward


def _backprop_precomputable_affine_padding(model, dY, ids):
    nB = dY.shape[0]
    nF = model.get_dim("nF")
    nP = model.get_dim("nP")
    nO = model.get_dim("nO")
    # Backprop the "padding", used as a filler for missing values.
    # Values that are missing are set to -1, and each state vector could
    # have multiple missing values. The padding has different values for
    # different missing features. The gradient of the padding vector is:
    #
    # for b in range(nB):
    #     for f in range(nF):
    #         if ids[b, f] < 0:
    #             d_pad[f] += dY[b]
    #
    # Which can be rewritten as:
    #
    # (ids < 0).T @ dY
    mask = model.ops.asarray(ids < 0, dtype="f")
    d_pad = model.ops.gemm(mask, dY.reshape(nB, nO * nP), trans1=True)
    return d_pad.reshape((1, nF, nO, nP))


def _infer_nO(Y: Optional[Tuple[List[State], List[Floats2d]]]) -> Optional[int]:
    if Y is None:
        return None
    _, scores = Y
    if len(scores) == 0:
        return None
    assert scores[0].shape[0] >= 1
    assert len(scores[0].shape) == 2
    return scores[0].shape[1]


def _lsuv_init(model):
    """This is like the 'layer sequential unit variance', but instead
    of taking the actual inputs, we randomly generate whitened data.

    Why's this all so complicated? We have a huge number of inputs,
    and the maxout unit makes guessing the dynamics tricky. Instead
    we set the maxout weights to values that empirically result in
    whitened outputs given whitened inputs.
    """
    # TODO
    return None
