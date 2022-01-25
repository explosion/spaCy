from typing import List, Tuple, Any, Optional, cast
from thinc.api import Ops, Model, normal_init, chain, list2array, Linear
from thinc.api import uniform_init, glorot_uniform_init, zero_init
from thinc.types import Floats1d, Floats2d, Floats3d, Ints2d, Floats4d
import numpy
from ..tokens.doc import Doc
from ..util import registry


TransitionSystem = Any  # TODO
State = Any  # TODO


@registry.layers("spacy.TransitionModel.v2")
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
    t2v_width = tok2vec.get_dim("nO") if tok2vec.has_dim("nO") else None
    tok2vec_projected = chain(tok2vec, list2array(), Linear(hidden_width, t2v_width))  # type: ignore
    tok2vec_projected.set_dim("nO", hidden_width)

    return Model(
        name="parser_model",
        forward=forward,
        init=init,
        layers=[tok2vec_projected],
        refs={"tok2vec": tok2vec_projected},
        params={
            "lower_W": None,  # Floats2d W for the hidden layer
            "lower_b": None,  # Floats1d bias for the hidden layer
            "lower_pad": None,  # Floats1d padding for the hidden layer
            "upper_W": None,  # Floats2d W for the output layer
            "upper_b": None,  # Floats1d bias for the output layer
        },
        dims={
            "nO": None,  # Output size
            "nP": maxout_pieces,
            "nH": hidden_width,
            "nI": tok2vec_projected.maybe_get_dim("nO"),
            "nF": state_tokens,
        },
        attrs={
            "unseen_classes": set(unseen_classes),
            "resize_output": resize_output,
        },
    )


def resize_output(model: Model, new_nO: int) -> Model:
    old_nO = model.maybe_get_dim("nO")
    if old_nO is None:
        model.set_dim("nO", new_nO)
        return model
    elif new_nO <= old_nO:
        return model
    elif model.has_param("upper_W"):
        nH = model.get_dim("nH")
        new_W = model.ops.alloc2f(new_nO, nH)
        new_b = model.ops.alloc1f(new_nO)
        old_W = model.get_param("upper_W")
        old_b = model.get_param("upper_b")
        new_W[:old_nO] = old_W  # type: ignore
        new_b[:old_nO] = old_b  # type: ignore
        for i in range(old_nO, new_nO):
            model.attrs["unseen_classes"].add(i)
        model.set_param("upper_W", new_W)
        model.set_param("upper_b", new_b)
    # TODO: Avoid this private intrusion
    model._dims["nO"] = new_nO
    if model.has_grad("upper_W"):
        model.set_grad("upper_W", model.get_param("upper_W") * 0)
    if model.has_grad("upper_b"):
        model.set_grad("upper_b", model.get_param("upper_b") * 0)
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

    Wl = ops.alloc2f(nH * nP, nF * nI)
    bl = ops.alloc1f(nH * nP)
    padl = ops.alloc1f(nI)
    Wu = ops.alloc2f(nO, nH)
    bu = ops.alloc1f(nO)
    Wu = zero_init(ops, Wu.shape)
    # Wl = zero_init(ops, Wl.shape)
    Wl = glorot_uniform_init(ops, Wl.shape)
    padl = uniform_init(ops, padl.shape)  # type: ignore
    # TODO: Experiment with whether better to initialize upper_W
    model.set_param("lower_W", Wl)
    model.set_param("lower_b", bl)
    model.set_param("lower_pad", padl)
    model.set_param("upper_W", Wu)
    model.set_param("upper_b", bu)
    # model = _lsuv_init(model)
    return model


def forward(model, docs_moves: Tuple[List[Doc], TransitionSystem], is_train: bool):
    nF = model.get_dim("nF")
    tok2vec = model.get_ref("tok2vec")
    lower_pad = model.get_param("lower_pad")
    lower_W = model.get_param("lower_W")
    lower_b = model.get_param("lower_b")
    upper_W = model.get_param("upper_W")
    upper_b = model.get_param("upper_b")
    nH = model.get_dim("nH")
    nP = model.get_dim("nP")
    nO = model.get_dim("nO")
    nI = model.get_dim("nI")

    ops = model.ops
    docs, moves = docs_moves
    states = moves.init_batch(docs)
    tokvecs, backprop_tok2vec = tok2vec(docs, is_train)
    tokvecs = model.ops.xp.vstack((tokvecs, lower_pad))
    feats, backprop_feats = _forward_precomputable_affine(model, tokvecs, is_train)
    all_ids = []
    all_which = []
    all_statevecs = []
    all_scores = []
    next_states = [s for s in states if not s.is_final()]
    unseen_mask = _get_unseen_mask(model)
    ids = numpy.zeros((len(states), nF), dtype="i")
    arange = model.ops.xp.arange(nF)
    while next_states:
        ids = ids[: len(next_states)]
        for i, state in enumerate(next_states):
            state.set_context_tokens(ids, i, nF)
        # Sum the state features, add the bias and apply the activation (maxout)
        # to create the state vectors.
        preacts2f = feats[ids, arange].sum(axis=1)  # type: ignore
        preacts2f += lower_b
        preacts = model.ops.reshape3f(preacts2f, preacts2f.shape[0], nH, nP)
        assert preacts.shape[0] == len(next_states), preacts.shape
        statevecs, which = ops.maxout(preacts)
        # Multiply the state-vector by the scores weights and add the bias,
        # to get the logits.
        scores = model.ops.gemm(statevecs, upper_W, trans2=True)
        scores += upper_b
        scores[:, unseen_mask == 0] = model.ops.xp.nanmin(scores)
        # Transition the states, filtering out any that are finished.
        cpu_scores = model.ops.to_numpy(scores)
        next_states = moves.transition_states(next_states, cpu_scores)
        all_scores.append(scores)
        if is_train:
            # Remember intermediate results for the backprop.
            all_ids.append(ids.copy())
            all_statevecs.append(statevecs)
            all_which.append(which)

    def backprop_parser(d_states_d_scores):
        d_tokvecs = model.ops.alloc2f(tokvecs.shape[0], tokvecs.shape[1])
        ids = model.ops.xp.vstack(all_ids)
        which = ops.xp.vstack(all_which)
        statevecs = model.ops.xp.vstack(all_statevecs)
        _, d_scores = d_states_d_scores
        if model.attrs.get("unseen_classes"):
            # If we have a negative gradient (i.e. the probability should
            # increase) on any classes we filtered out as unseen, mark
            # them as seen.
            for clas in set(model.attrs["unseen_classes"]):
                if (d_scores[:, clas] < 0).any():
                    model.attrs["unseen_classes"].remove(clas)
        d_scores *= unseen_mask
        # Calculate the gradients for the parameters of the upper layer.
        # The weight gemm is (nS, nO) @ (nS, nH).T
        model.inc_grad("upper_b", d_scores.sum(axis=0))
        model.inc_grad("upper_W", model.ops.gemm(d_scores, statevecs, trans1=True))
        # Now calculate d_statevecs, by backproping through the upper linear layer.
        # This gemm is (nS, nO) @ (nO, nH)
        d_statevecs = model.ops.gemm(d_scores, upper_W)
        # Backprop through the maxout activation
        d_preacts = model.ops.backprop_maxout(d_statevecs, which, nP)
        d_preacts2f = model.ops.reshape2f(d_preacts, d_preacts.shape[0], nH * nP)
        model.inc_grad("lower_b", d_preacts2f.sum(axis=0))
        # We don't need to backprop the summation, because we pass back the IDs instead
        d_state_features = backprop_feats((d_preacts2f, ids))
        d_tokvecs = model.ops.alloc2f(tokvecs.shape[0], tokvecs.shape[1])
        model.ops.scatter_add(d_tokvecs, ids, d_state_features)
        model.inc_grad("lower_pad", d_tokvecs[-1])
        return (backprop_tok2vec(d_tokvecs[:-1]), None)

    return (states, all_scores), backprop_parser


def _forward_reference(
    model, docs_moves: Tuple[List[Doc], TransitionSystem], is_train: bool
):
    """Slow reference implementation, without the precomputation"""
    nF = model.get_dim("nF")
    tok2vec = model.get_ref("tok2vec")
    lower_pad = model.get_param("lower_pad")
    lower_W = model.get_param("lower_W")
    lower_b = model.get_param("lower_b")
    upper_W = model.get_param("upper_W")
    upper_b = model.get_param("upper_b")
    nH = model.get_dim("nH")
    nP = model.get_dim("nP")
    nO = model.get_dim("nO")
    nI = model.get_dim("nI")

    ops = model.ops
    docs, moves = docs_moves
    states = moves.init_batch(docs)
    tokvecs, backprop_tok2vec = tok2vec(docs, is_train)
    tokvecs = model.ops.xp.vstack((tokvecs, lower_pad))
    all_ids = []
    all_which = []
    all_statevecs = []
    all_scores = []
    all_tokfeats = []
    next_states = [s for s in states if not s.is_final()]
    unseen_mask = _get_unseen_mask(model)
    ids = numpy.zeros((len(states), nF), dtype="i")
    while next_states:
        ids = ids[: len(next_states)]
        for i, state in enumerate(next_states):
            state.set_context_tokens(ids, i, nF)
        # Sum the state features, add the bias and apply the activation (maxout)
        # to create the state vectors.
        tokfeats3f = tokvecs[ids]
        tokfeats = model.ops.reshape2f(tokfeats3f, tokfeats3f.shape[0], -1)
        preacts2f = model.ops.gemm(tokfeats, lower_W, trans2=True)
        preacts2f += lower_b
        preacts = model.ops.reshape3f(preacts2f, preacts2f.shape[0], nH, nP)
        statevecs, which = ops.maxout(preacts)
        # Multiply the state-vector by the scores weights and add the bias,
        # to get the logits.
        scores = model.ops.gemm(statevecs, upper_W, trans2=True)
        scores += upper_b
        scores[:, unseen_mask == 0] = model.ops.xp.nanmin(scores)
        # Transition the states, filtering out any that are finished.
        next_states = moves.transition_states(next_states, scores)
        all_scores.append(scores)
        if is_train:
            # Remember intermediate results for the backprop.
            all_tokfeats.append(tokfeats)
            all_ids.append(ids.copy())
            all_statevecs.append(statevecs)
            all_which.append(which)

    nS = sum(len(s.history) for s in states)

    def backprop_parser(d_states_d_scores):
        d_tokvecs = model.ops.alloc2f(tokvecs.shape[0], tokvecs.shape[1])
        ids = model.ops.xp.vstack(all_ids)
        which = ops.xp.vstack(all_which)
        statevecs = model.ops.xp.vstack(all_statevecs)
        tokfeats = model.ops.xp.vstack(all_tokfeats)
        _, d_scores = d_states_d_scores
        if model.attrs.get("unseen_classes"):
            # If we have a negative gradient (i.e. the probability should
            # increase) on any classes we filtered out as unseen, mark
            # them as seen.
            for clas in set(model.attrs["unseen_classes"]):
                if (d_scores[:, clas] < 0).any():
                    model.attrs["unseen_classes"].remove(clas)
        d_scores *= unseen_mask
        assert statevecs.shape == (nS, nH), statevecs.shape
        assert d_scores.shape == (nS, nO), d_scores.shape
        # Calculate the gradients for the parameters of the upper layer.
        # The weight gemm is (nS, nO) @ (nS, nH).T
        model.inc_grad("upper_b", d_scores.sum(axis=0))
        model.inc_grad("upper_W", model.ops.gemm(d_scores, statevecs, trans1=True))
        # Now calculate d_statevecs, by backproping through the upper linear layer.
        # This gemm is (nS, nO) @ (nO, nH)
        d_statevecs = model.ops.gemm(d_scores, upper_W)
        # Backprop through the maxout activation
        d_preacts = model.ops.backprop_maxout(d_statevecs, which, nP)
        d_preacts2f = model.ops.reshape2f(d_preacts, d_preacts.shape[0], nH * nP)
        # Now increment the gradients for the lower layer.
        # The gemm here is (nS, nH*nP) @ (nS, nF*nI)
        model.inc_grad("lower_b", d_preacts2f.sum(axis=0))
        model.inc_grad("lower_W", model.ops.gemm(d_preacts2f, tokfeats, trans1=True))
        # Caclulate d_tokfeats
        # The gemm here is (nS, nH*nP) @ (nH*nP, nF*nI)
        d_tokfeats = model.ops.gemm(d_preacts2f, lower_W)
        # Get the gradients of the tokvecs and the padding
        d_tokfeats3f = model.ops.reshape3f(d_tokfeats, nS, nF, nI)
        model.ops.scatter_add(d_tokvecs, ids, d_tokfeats3f)
        model.inc_grad("lower_pad", d_tokvecs[-1])
        return (backprop_tok2vec(d_tokvecs[:-1]), None)

    return (states, all_scores), backprop_parser


def _get_unseen_mask(model: Model) -> Floats1d:
    mask = model.ops.alloc1f(model.get_dim("nO"))
    mask.fill(1)
    for class_ in model.attrs.get("unseen_classes", set()):
        mask[class_] = 0
    return mask


def _forward_precomputable_affine(model, X: Floats2d, is_train: bool):
    W: Floats2d = model.get_param("lower_W")
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
        model.inc_grad("lower_W", dW)
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
    W = model.maybe_get_param("lower_W")
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
    W = cast(Floats4d, model.get_param("lower_W").copy())
    b = cast(Floats2d, model.get_param("lower_b").copy())
    for t_i in range(t_max):
        acts1 = predict(ids, tokvecs)
        var = model.ops.xp.var(acts1)
        mean = model.ops.xp.mean(acts1)
        if abs(var - 1.0) >= tol_var:
            W /= model.ops.xp.sqrt(var)
            model.set_param("lower_W", W)
        elif abs(mean) >= tol_mean:
            b -= mean
            model.set_param("lower_b", b)
        else:
            break
    return model
