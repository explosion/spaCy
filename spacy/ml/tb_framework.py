from thinc.api import Model, noop, use_ops, Linear
from .parser_model import ParserStepModel


def TransitionModel(tok2vec, lower, upper, dropout=0.2, unseen_classes=set()):
    """Set up a stepwise transition-based model"""
    if upper is None:
        has_upper = False
        upper = noop()
    else:
        has_upper = True
    # don't define nO for this object, because we can't dynamically change it
    return Model(
        name="parser_model",
        forward=forward,
        dims={"nI": tok2vec.get_dim("nI") if tok2vec.has_dim("nI") else None},
        layers=[tok2vec, lower, upper],
        refs={"tok2vec": tok2vec, "lower": lower, "upper": upper},
        init=init,
        attrs={
            "has_upper": has_upper,
            "unseen_classes": set(unseen_classes),
            "resize_output": resize_output,
        },
    )


def forward(model, X, is_train):
    step_model = ParserStepModel(
        X,
        model.layers,
        unseen_classes=model.attrs["unseen_classes"],
        train=is_train,
        has_upper=model.attrs["has_upper"],
    )

    return step_model, step_model.finish_steps


def init(model, X=None, Y=None):
    model.get_ref("tok2vec").initialize(X=X)
    lower = model.get_ref("lower")
    lower.initialize()
    if model.attrs["has_upper"]:
        statevecs = model.ops.alloc2f(2, lower.get_dim("nO"))
        model.get_ref("upper").initialize(X=statevecs)


def resize_output(model, new_nO):
    lower = model.get_ref("lower")
    upper = model.get_ref("upper")
    if not model.attrs["has_upper"]:
        if lower.has_dim("nO") is None:
            lower.set_dim("nO", new_nO)
        return
    elif upper.has_dim("nO") is None:
        upper.set_dim("nO", new_nO)
        return
    elif new_nO == upper.get_dim("nO"):
        return
    smaller = upper
    nI = None
    if smaller.has_dim("nI"):
        nI = smaller.get_dim("nI")
    with use_ops("numpy"):
        larger = Linear(nO=new_nO, nI=nI)
        larger.init = smaller.init
    # it could be that the model is not initialized yet, then skip this bit
    if nI:
        larger_W = larger.ops.alloc2f(new_nO, nI)
        larger_b = larger.ops.alloc1f(new_nO)
        smaller_W = smaller.get_param("W")
        smaller_b = smaller.get_param("b")
        # Weights are stored in (nr_out, nr_in) format, so we're basically
        # just adding rows here.
        if smaller.has_dim("nO"):
            larger_W[: smaller.get_dim("nO")] = smaller_W
            larger_b[: smaller.get_dim("nO")] = smaller_b
            for i in range(smaller.get_dim("nO"), new_nO):
                model.attrs["unseen_classes"].add(i)

        larger.set_param("W", larger_W)
        larger.set_param("b", larger_b)
    model._layers[-1] = larger
    model.set_ref("upper", larger)
    return model
