from functools import partial
from typing import List, Optional, Tuple, cast

from thinc.api import (
    Dropout,
    Gelu,
    LayerNorm,
    Linear,
    Logistic,
    Maxout,
    Model,
    ParametricAttention,
    ParametricAttention_v2,
    Relu,
    Softmax,
    SparseLinear,
    SparseLinear_v2,
    chain,
    clone,
    concatenate,
    list2ragged,
    reduce_first,
    reduce_last,
    reduce_max,
    reduce_mean,
    reduce_sum,
    residual,
    resizable,
    softmax_activation,
    with_cpu,
)
from thinc.layers.chain import init as init_chain
from thinc.layers.resizable import resize_linear_weighted, resize_model
from thinc.types import ArrayXd, Floats2d

from ...attrs import ORTH
from ...errors import Errors
from ...tokens import Doc
from ...util import registry
from ..extract_ngrams import extract_ngrams
from ..staticvectors import StaticVectors
from .tok2vec import get_tok2vec_width

NEG_VALUE = -5000


def build_simple_cnn_text_classifier(
    tok2vec: Model, exclusive_classes: bool, nO: Optional[int] = None
) -> Model[List[Doc], Floats2d]:
    """
    Build a simple CNN text classifier, given a token-to-vector model as inputs.
    If exclusive_classes=True, a softmax non-linearity is applied, so that the
    outputs sum to 1. If exclusive_classes=False, a logistic non-linearity
    is applied instead, so that outputs are in the range [0, 1].
    """
    return build_reduce_text_classifier(
        tok2vec=tok2vec,
        exclusive_classes=exclusive_classes,
        use_reduce_first=False,
        use_reduce_last=False,
        use_reduce_max=False,
        use_reduce_mean=True,
        nO=nO,
    )


def resize_and_set_ref(model, new_nO, resizable_layer):
    resizable_layer = resize_model(resizable_layer, new_nO)
    model.set_ref("output_layer", resizable_layer.layers[0])
    model.set_dim("nO", new_nO, force=True)
    return model


def build_bow_text_classifier(
    exclusive_classes: bool,
    ngram_size: int,
    no_output_layer: bool,
    nO: Optional[int] = None,
) -> Model[List[Doc], Floats2d]:
    return _build_bow_text_classifier(
        exclusive_classes=exclusive_classes,
        ngram_size=ngram_size,
        no_output_layer=no_output_layer,
        nO=nO,
        sparse_linear=SparseLinear(nO=nO),
    )


def build_bow_text_classifier_v3(
    exclusive_classes: bool,
    ngram_size: int,
    no_output_layer: bool,
    length: int = 262144,
    nO: Optional[int] = None,
) -> Model[List[Doc], Floats2d]:
    if length < 1:
        raise ValueError(Errors.E1056.format(length=length))

    # Find k such that 2**(k-1) < length <= 2**k.
    length = 2 ** (length - 1).bit_length()

    return _build_bow_text_classifier(
        exclusive_classes=exclusive_classes,
        ngram_size=ngram_size,
        no_output_layer=no_output_layer,
        nO=nO,
        sparse_linear=SparseLinear_v2(nO=nO, length=length),
    )


def _build_bow_text_classifier(
    exclusive_classes: bool,
    ngram_size: int,
    no_output_layer: bool,
    sparse_linear: Model[Tuple[ArrayXd, ArrayXd, ArrayXd], ArrayXd],
    nO: Optional[int] = None,
) -> Model[List[Doc], Floats2d]:
    fill_defaults = {"b": 0, "W": 0}
    with Model.define_operators({">>": chain}):
        output_layer = None
        if not no_output_layer:
            fill_defaults["b"] = NEG_VALUE
            output_layer = softmax_activation() if exclusive_classes else Logistic()
        resizable_layer: Model[Floats2d, Floats2d] = resizable(
            sparse_linear,
            resize_layer=partial(resize_linear_weighted, fill_defaults=fill_defaults),
        )
        model = extract_ngrams(ngram_size, attr=ORTH) >> resizable_layer
        model = with_cpu(model, model.ops)
        if output_layer:
            model = model >> with_cpu(output_layer, output_layer.ops)
    if nO is not None:
        model.set_dim("nO", cast(int, nO))
    model.set_ref("output_layer", sparse_linear)
    model.attrs["multi_label"] = not exclusive_classes
    model.attrs["resize_output"] = partial(
        resize_and_set_ref, resizable_layer=resizable_layer
    )
    return model


def build_text_classifier_v2(
    tok2vec: Model[List[Doc], List[Floats2d]],
    linear_model: Model[List[Doc], Floats2d],
    nO: Optional[int] = None,
) -> Model[List[Doc], Floats2d]:
    # TODO: build the model with _build_parametric_attention_with_residual_nonlinear
    # in spaCy v4. We don't do this in spaCy v3 to preserve model
    # compatibility.
    exclusive_classes = not linear_model.attrs["multi_label"]
    with Model.define_operators({">>": chain, "|": concatenate}):
        width = tok2vec.maybe_get_dim("nO")
        attention_layer = ParametricAttention(width)
        maxout_layer = Maxout(nO=width, nI=width)
        norm_layer = LayerNorm(nI=width)
        cnn_model = (
            tok2vec
            >> list2ragged()
            >> attention_layer
            >> reduce_sum()
            >> residual(maxout_layer >> norm_layer >> Dropout(0.0))
        )

        nO_double = nO * 2 if nO else None
        if exclusive_classes:
            output_layer = Softmax(nO=nO, nI=nO_double)
        else:
            output_layer = Linear(nO=nO, nI=nO_double) >> Logistic()
        model = (linear_model | cnn_model) >> output_layer
        model.set_ref("tok2vec", tok2vec)
    if model.has_dim("nO") is not False and nO is not None:
        model.set_dim("nO", cast(int, nO))
    model.set_ref("output_layer", linear_model.get_ref("output_layer"))
    model.set_ref("attention_layer", attention_layer)
    model.set_ref("maxout_layer", maxout_layer)
    model.set_ref("norm_layer", norm_layer)
    model.attrs["multi_label"] = not exclusive_classes

    model.init = init_ensemble_textcat  # type: ignore[assignment]
    return model


def init_ensemble_textcat(model, X, Y) -> Model:
    # When tok2vec is lazily initialized, we need to initialize it before
    # the rest of the chain to ensure that we can get its width.
    tok2vec = model.get_ref("tok2vec")
    tok2vec.initialize(X)

    tok2vec_width = get_tok2vec_width(model)
    model.get_ref("attention_layer").set_dim("nO", tok2vec_width)
    model.get_ref("maxout_layer").set_dim("nO", tok2vec_width)
    model.get_ref("maxout_layer").set_dim("nI", tok2vec_width)
    model.get_ref("norm_layer").set_dim("nI", tok2vec_width)
    model.get_ref("norm_layer").set_dim("nO", tok2vec_width)
    init_chain(model, X, Y)
    return model


def build_text_classifier_lowdata(
    width: int, dropout: Optional[float], nO: Optional[int] = None
) -> Model[List[Doc], Floats2d]:
    # Don't document this yet, I'm not sure it's right.
    # Note, before v.3, this was the default if setting "low_data" and "pretrained_dims"
    with Model.define_operators({">>": chain, "**": clone}):
        model = (
            StaticVectors(width)
            >> list2ragged()
            >> ParametricAttention(width)
            >> reduce_sum()
            >> residual(Relu(width, width)) ** 2
            >> Linear(nO, width)
        )
        if dropout:
            model = model >> Dropout(dropout)
        model = model >> Logistic()
    return model


def build_textcat_parametric_attention_v1(
    tok2vec: Model[List[Doc], List[Floats2d]],
    exclusive_classes: bool,
    nO: Optional[int] = None,
) -> Model[List[Doc], Floats2d]:
    width = tok2vec.maybe_get_dim("nO")
    parametric_attention = _build_parametric_attention_with_residual_nonlinear(
        tok2vec=tok2vec,
        nonlinear_layer=Maxout(nI=width, nO=width),
        key_transform=Gelu(nI=width, nO=width),
    )
    with Model.define_operators({">>": chain}):
        if exclusive_classes:
            output_layer = Softmax(nO=nO)
        else:
            output_layer = Linear(nO=nO) >> Logistic()
        model = parametric_attention >> output_layer
    if model.has_dim("nO") is not False and nO is not None:
        model.set_dim("nO", cast(int, nO))
    model.set_ref("output_layer", output_layer)
    model.attrs["multi_label"] = not exclusive_classes

    return model


def _build_parametric_attention_with_residual_nonlinear(
    *,
    tok2vec: Model[List[Doc], List[Floats2d]],
    nonlinear_layer: Model[Floats2d, Floats2d],
    key_transform: Optional[Model[Floats2d, Floats2d]] = None,
) -> Model[List[Doc], Floats2d]:
    with Model.define_operators({">>": chain, "|": concatenate}):
        width = tok2vec.maybe_get_dim("nO")
        attention_layer = ParametricAttention_v2(nO=width, key_transform=key_transform)
        norm_layer = LayerNorm(nI=width)
        parametric_attention = (
            tok2vec
            >> list2ragged()
            >> attention_layer
            >> reduce_sum()
            >> residual(nonlinear_layer >> norm_layer >> Dropout(0.0))
        )

        parametric_attention.init = _init_parametric_attention_with_residual_nonlinear

        parametric_attention.set_ref("tok2vec", tok2vec)
        parametric_attention.set_ref("attention_layer", attention_layer)
        parametric_attention.set_ref("key_transform", key_transform)
        parametric_attention.set_ref("nonlinear_layer", nonlinear_layer)
        parametric_attention.set_ref("norm_layer", norm_layer)

        return parametric_attention


def _init_parametric_attention_with_residual_nonlinear(model, X, Y) -> Model:
    # When tok2vec is lazily initialized, we need to initialize it before
    # the rest of the chain to ensure that we can get its width.
    tok2vec = model.get_ref("tok2vec")
    tok2vec.initialize(X)

    tok2vec_width = get_tok2vec_width(model)
    model.get_ref("attention_layer").set_dim("nO", tok2vec_width)
    model.get_ref("key_transform").set_dim("nI", tok2vec_width)
    model.get_ref("key_transform").set_dim("nO", tok2vec_width)
    model.get_ref("nonlinear_layer").set_dim("nI", tok2vec_width)
    model.get_ref("nonlinear_layer").set_dim("nO", tok2vec_width)
    model.get_ref("norm_layer").set_dim("nI", tok2vec_width)
    model.get_ref("norm_layer").set_dim("nO", tok2vec_width)
    init_chain(model, X, Y)
    return model


def build_reduce_text_classifier(
    tok2vec: Model,
    exclusive_classes: bool,
    use_reduce_first: bool,
    use_reduce_last: bool,
    use_reduce_max: bool,
    use_reduce_mean: bool,
    nO: Optional[int] = None,
) -> Model[List[Doc], Floats2d]:
    """Build a model that classifies pooled `Doc` representations.

    Pooling is performed using reductions. Reductions are concatenated when
    multiple reductions are used.

    tok2vec (Model): the tok2vec layer to pool over.
    exclusive_classes (bool): Whether or not classes are mutually exclusive.
    use_reduce_first (bool): Pool by using the hidden representation of the
        first token of a `Doc`.
    use_reduce_last (bool): Pool by using the hidden representation of the
        last token of a `Doc`.
    use_reduce_max (bool): Pool by taking the maximum values of the hidden
        representations of a `Doc`.
    use_reduce_mean (bool): Pool by taking the mean of all hidden
        representations of a `Doc`.
    nO (Optional[int]): Number of classes.
    """

    fill_defaults = {"b": 0, "W": 0}
    reductions = []
    if use_reduce_first:
        reductions.append(reduce_first())
    if use_reduce_last:
        reductions.append(reduce_last())
    if use_reduce_max:
        reductions.append(reduce_max())
    if use_reduce_mean:
        reductions.append(reduce_mean())

    if not len(reductions):
        raise ValueError(Errors.E1057)

    with Model.define_operators({">>": chain}):
        cnn = tok2vec >> list2ragged() >> concatenate(*reductions)
        nO_tok2vec = tok2vec.maybe_get_dim("nO")
        nI = nO_tok2vec * len(reductions) if nO_tok2vec is not None else None
        if exclusive_classes:
            output_layer = Softmax(nO=nO, nI=nI)
            fill_defaults["b"] = NEG_VALUE
            resizable_layer: Model = resizable(
                output_layer,
                resize_layer=partial(
                    resize_linear_weighted, fill_defaults=fill_defaults
                ),
            )
            model = cnn >> resizable_layer
        else:
            output_layer = Linear(nO=nO, nI=nI)
            resizable_layer = resizable(
                output_layer,
                resize_layer=partial(
                    resize_linear_weighted, fill_defaults=fill_defaults
                ),
            )
            model = cnn >> resizable_layer >> Logistic()
        model.set_ref("output_layer", output_layer)
        model.attrs["resize_output"] = partial(
            resize_and_set_ref,
            resizable_layer=resizable_layer,
        )
    model.set_ref("tok2vec", tok2vec)
    if nO is not None:
        model.set_dim("nO", cast(int, nO))
    model.attrs["multi_label"] = not exclusive_classes
    return model
