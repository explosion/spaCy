from functools import partial
from typing import Optional, List

from thinc.types import Floats2d
from thinc.api import Model, reduce_mean, Linear, list2ragged, Logistic
from thinc.api import chain, concatenate, clone, Dropout, ParametricAttention
from thinc.api import SparseLinear, Softmax, softmax_activation, Maxout, reduce_sum
from thinc.api import with_cpu, Relu, residual, LayerNorm
from thinc.layers.chain import init as init_chain

from ...attrs import ORTH
from ...util import registry
from ..extract_ngrams import extract_ngrams
from ..staticvectors import StaticVectors
from ...tokens import Doc
from .tok2vec import get_tok2vec_width


# TODO: to legacy
@registry.architectures("spacy.TextCatCNN.v1")
def build_simple_cnn_text_classifier_v1(
    tok2vec: Model, exclusive_classes: bool, nO: Optional[int] = None
) -> Model[List[Doc], Floats2d]:
    """
    Build a simple CNN text classifier, given a token-to-vector model as inputs.
    If exclusive_classes=True, a softmax non-linearity is applied, so that the
    outputs sum to 1. If exclusive_classes=False, a logistic non-linearity
    is applied instead, so that outputs are in the range [0, 1].
    """
    with Model.define_operators({">>": chain}):
        cnn = tok2vec >> list2ragged() >> reduce_mean()
        if exclusive_classes:
            output_layer = Softmax(nO=nO, nI=tok2vec.maybe_get_dim("nO"))
            model = cnn >> output_layer
            model.set_ref("output_layer", output_layer)
        else:
            linear_layer = Linear(nO=nO, nI=tok2vec.maybe_get_dim("nO"))
            model = cnn >> linear_layer >> Logistic()
            model.set_ref("output_layer", linear_layer)
    model.set_ref("tok2vec", tok2vec)
    model.set_dim("nO", nO)
    model.attrs["multi_label"] = not exclusive_classes
    return model


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
    cnn = chain(tok2vec, list2ragged(), reduce_mean())
    if exclusive_classes:
        output_layer = _create_output_cnn_excl(nO=nO, nI=tok2vec.maybe_get_dim("nO"))
        model = chain(cnn, output_layer)
        model.set_ref("output_layer", output_layer)
        model.attrs["resize_output"] = partial(_resize_cnn,
                                               create_output=_create_output_cnn_excl,
                                               index=-1)
    else:
        linear_layer = _create_output_cnn_not_excl(nO=nO, nI=tok2vec.maybe_get_dim("nO"))
        model = chain(cnn, linear_layer, Logistic())
        model.set_ref("output_layer", linear_layer)
        model.attrs["resize_output"] = partial(_resize_cnn,
                                               create_output=_create_output_cnn_not_excl,
                                               index=-2)

    model.set_ref("tok2vec", tok2vec)
    model.set_dim("nO", nO)
    model.attrs["multi_label"] = not exclusive_classes
    return model


def _create_output_cnn_excl(nO, nI):
    return Softmax(nO=nO, nI=nI)


def _create_output_cnn_not_excl(nO, nI):
    return Linear(nO=nO, nI=nI)


def _resize_cnn(model, new_nO, create_output, index):
    output_layer = model.get_ref("output_layer")
    if output_layer.has_dim("nO") is None:
        # the output layer had not been initialized/trained yet
        output_layer.set_dim("nO", new_nO)
        return model
    elif new_nO == output_layer.get_dim("nO"):
        # the dimensions didn't change
        return model

    # create a new, larger output layer and copy the weights over from the smaller one
    smaller = output_layer
    nI = model.get_ref("tok2vec").maybe_get_dim("nO")
    larger = create_output(nO=new_nO, nI=nI)
    assert larger.get_dim("nO") > smaller.get_dim("nO")

    # it could be that the model is not initialized yet, then skip this bit
    if smaller.has_param("W"):
        larger_W = larger.ops.alloc2f(new_nO, nI)
        larger_b = larger.ops.alloc1f(new_nO)
        smaller_W = smaller.get_param("W")
        smaller_b = smaller.get_param("b")
        # Weights are stored in (nr_out, nr_in) format, so we're basically
        # just adding rows here.
        old_nO = smaller.get_dim("nO")
        larger_W[:old_nO] = smaller_W
        larger_b[:old_nO] = smaller_b
        larger.set_param("W", larger_W)
        larger.set_param("b", larger_b)
    model._layers[index] = larger
    model.set_ref("output_layer", larger)
    if model.has_dim("nO"):
        model.set_dim("nO", new_nO, force=True)
    return model


@registry.architectures("spacy.TextCatBOW.v1")
def build_bow_text_classifier(
    exclusive_classes: bool,
    ngram_size: int,
    no_output_layer: bool,
    nO: Optional[int] = None,
) -> Model[List[Doc], Floats2d]:
    with Model.define_operators({">>": chain}):
        sparse_linear = SparseLinear(nO)
        model = extract_ngrams(ngram_size, attr=ORTH) >> sparse_linear
        model = with_cpu(model, model.ops)
        if not no_output_layer:
            output_layer = softmax_activation() if exclusive_classes else Logistic()
            model = model >> with_cpu(output_layer, output_layer.ops)
    model.set_dim("nO", nO)
    model.set_ref("output_layer", sparse_linear)
    model.attrs["multi_label"] = not exclusive_classes
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
        attention_layer = ParametricAttention(
            width
        )  # TODO: benchmark performance difference of this layer
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
    if model.has_dim("nO") is not False:
        model.set_dim("nO", nO)
    model.set_ref("output_layer", linear_model.get_ref("output_layer"))
    model.set_ref("attention_layer", attention_layer)
    model.set_ref("maxout_layer", maxout_layer)
    model.set_ref("norm_layer", norm_layer)
    model.attrs["multi_label"] = not exclusive_classes

    model.init = init_ensemble_textcat
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
