from typing import Optional, List, cast
from functools import partial

from thinc.types import Floats2d
from thinc.api import Model, reduce_mean, Linear, list2ragged, Logistic
from thinc.api import chain, concatenate, clone, Dropout, ParametricAttention
from thinc.api import SparseLinear, Softmax, softmax_activation, Maxout, reduce_sum
from thinc.api import with_cpu, Relu, residual, LayerNorm, resizable
from thinc.layers.chain import init as init_chain
from thinc.layers.resizable import resize_model, resize_linear_weighted

from ...attrs import ORTH
from ...util import registry
from ..extract_ngrams import extract_ngrams
from ..staticvectors import StaticVectors
from ...tokens import Doc
from .tok2vec import get_tok2vec_width


NEG_VALUE = -5000


@registry.architectures("spacy.TextCatCNN.v2")
def build_simple_cnn_text_classifier(
    tok2vec: Model, exclusive_classes: bool, nO: Optional[int] = None
) -> Model[List[Doc], Floats2d]:
    """
    Build a simple CNN text classifier, given a token-to-vector model as inputs.
    If exclusive_classes=True, a softmax non-linearity is applied, so that the
    outputs sum to 1. If exclusive_classes=False, a logistic non-linearity
    is applied instead, so that outputs are in the range [0, 1].
    """
    fill_defaults = {"b": 0, "W": 0}
    with Model.define_operators({">>": chain}):
        cnn = tok2vec >> list2ragged() >> reduce_mean()
        nI = tok2vec.maybe_get_dim("nO")
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


def resize_and_set_ref(model, new_nO, resizable_layer):
    resizable_layer = resize_model(resizable_layer, new_nO)
    model.set_ref("output_layer", resizable_layer.layers[0])
    model.set_dim("nO", new_nO, force=True)
    return model


@registry.architectures("spacy.TextCatBOW.v2")
def build_bow_text_classifier(
    exclusive_classes: bool,
    ngram_size: int,
    no_output_layer: bool,
    nO: Optional[int] = None,
) -> Model[List[Doc], Floats2d]:
    fill_defaults = {"b": 0, "W": 0}
    with Model.define_operators({">>": chain}):
        sparse_linear = SparseLinear(nO=nO)
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


@registry.architectures("spacy.TextCatEnsemble.v2")
def build_text_classifier_v2(
    tok2vec: Model[List[Doc], List[Floats2d]],
    linear_model: Model[List[Doc], Floats2d],
    nO: Optional[int] = None,
) -> Model[List[Doc], Floats2d]:
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
    tok2vec_width = get_tok2vec_width(model)
    model.get_ref("attention_layer").set_dim("nO", tok2vec_width)
    model.get_ref("maxout_layer").set_dim("nO", tok2vec_width)
    model.get_ref("maxout_layer").set_dim("nI", tok2vec_width)
    model.get_ref("norm_layer").set_dim("nI", tok2vec_width)
    model.get_ref("norm_layer").set_dim("nO", tok2vec_width)
    init_chain(model, X, Y)
    return model


@registry.architectures("spacy.TextCatLowData.v1")
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
