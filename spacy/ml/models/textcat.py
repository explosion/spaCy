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
    cnn = chain(tok2vec, list2ragged(), reduce_mean())
    nI = tok2vec.maybe_get_dim("nO")
    if exclusive_classes:
        output_layer = Softmax(nO=nO, nI=nI)
        model = chain(cnn, output_layer)
        model.set_ref("output_layer", output_layer)
        model.attrs["activation"] = "softmax"
        model.attrs["resize_output"] = partial(
            _resize_layer, layer=output_layer
        )
    else:
        linear_layer = Linear(nO=nO, nI=tok2vec.maybe_get_dim("nO"))
        model = chain(cnn, linear_layer, Logistic())
        model.set_ref("output_layer", linear_layer)
        model.attrs["activation"] = "linear"
        model.attrs["resize_output"] = partial(
            _resize_layer, layer=linear_layer
        )

    model.set_ref("tok2vec", tok2vec)
    model.set_dim("nO", nO)
    model.attrs["multi_label"] = not exclusive_classes
    return model


def _resize_layer(model, new_nO, layer):
    """ Resize a typical layer with 2D W and 1D b parameters"""
    if layer.has_dim("nO") is None:
        # the output layer had not been initialized/trained yet
        layer.set_dim("nO", new_nO)
        return model
    elif new_nO == layer.get_dim("nO"):
        # the dimensions didn't change
        return model

    old_nO = layer.get_dim("nO")
    assert new_nO > old_nO

    # it could be that the model is not initialized yet, then skip this bit
    if layer.has_param("b"):
        larger_b = layer.ops.alloc1f(new_nO)
        smaller_b = layer.get_param("b")
        larger_b[:old_nO] = smaller_b
        if "activation" in model.attrs and model.attrs["activation"] in ["softmax", "logistic"]:
            # ensure little influence on the softmax/logistic activation
            larger_b[old_nO:] = NEG_VALUE
        layer.set_param("b", larger_b)

    if layer.has_param("W"):
        old_nI = layer.get_dim("nI")
        new_nI = layer.get_dim("nI")
        assert new_nI >= old_nI
        larger_W = layer.ops.alloc2f(new_nO, new_nI)
        smaller_W = layer.get_param("W")
        # Copy the old weights into the new weight tensor
        larger_W[:old_nO, :old_nI] = smaller_W
        layer.set_param("W", larger_W)
        layer.set_dim("nI", new_nI, force=True)

    layer.set_dim("nO", new_nO, force=True)
    if model:
        model.set_dim("nO", new_nO, force=True)
    return model


def _resize_concatting_layer(model, new_nO, layer, input_layers):
    """ Resize a concatting layer with 2D W and 1D b parameters"""
    if layer.has_dim("nO") is None:
        # the output layer had not been initialized/trained yet
        layer.set_dim("nO", new_nO)
        return model
    elif new_nO == layer.get_dim("nO"):
        # the dimensions didn't change
        return model

    old_nO = layer.get_dim("nO")
    assert new_nO > old_nO

    # it could be that the model is not initialized yet, then skip this bit
    if layer.has_param("b"):
        larger_b = layer.ops.alloc1f(new_nO)
        smaller_b = layer.get_param("b")
        larger_b[:old_nO] = smaller_b
        if "activation" in model.attrs and model.attrs["activation"] in ["softmax", "logistic"]:
            # ensure little influence on the softmax/logistic activation
            larger_b[old_nO:] = NEG_VALUE
        layer.set_param("b", larger_b)

    if layer.has_param("W"):
        old_nI = layer.get_dim("nI")
        new_nI = new_nO * input_layers
        old_input_nI = int(old_nI / input_layers)
        new_input_nI = int(new_nI / input_layers)
        assert new_nI >= old_nI
        larger_W = layer.ops.alloc2f(new_nO, new_nI)
        smaller_W = layer.get_param("W")
        # Copy the old weights into the new weight tensor
        input_offset = 0
        output_offset = 0
        for _ in range(input_layers):
            larger_W[0:old_nO,output_offset:output_offset+old_input_nI] = smaller_W[:,input_offset:input_offset+old_input_nI]
            input_offset += old_input_nI
            output_offset += new_input_nI

        layer.set_param("W", larger_W)
        layer.set_dim("nI", new_nI, force=True)

    layer.set_dim("nO", new_nO, force=True)
    if model:
        model.set_dim("nO", new_nO, force=True)
    return model


@registry.architectures("spacy.TextCatBOW.v2")
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
        activation = "linear"
        if not no_output_layer:
            if exclusive_classes:
                output_layer = softmax_activation()
                activation = "softmax"
            else:
                output_layer = Logistic()
                activation = "logistic"
            model = model >> with_cpu(output_layer, output_layer.ops)
    model.set_dim("nO", nO)
    model.set_ref("output_layer", sparse_linear)
    model.attrs["multi_label"] = not exclusive_classes
    model.attrs["activation"] = activation
    model.attrs["resize_output"] = partial(_resize_bow, layer=sparse_linear)
    return model


def _resize_bow(model, new_nO, layer):
    """ Resize a BOW output layer (using SparseLinear) in-place"""
    if layer.has_dim("nO") is None:
        # the output layer had not been initialized/trained yet
        layer.set_dim("nO", new_nO)
        return model
    elif new_nO == layer.get_dim("nO"):
        # the dimensions didn't change
        return model

    length = layer.get_dim("length")
    old_nO = layer.get_dim("nO")
    assert new_nO > old_nO

    # it could be that the model is not initialized yet, then skip this bit
    if layer.has_param("W"):
        larger_W = layer.ops.alloc1f(new_nO * length)
        larger_b = layer.ops.alloc1f(new_nO)
        smaller_W = layer.get_param("W")
        smaller_b = layer.get_param("b")
        larger_W[:old_nO*length] = smaller_W
        larger_b[:old_nO] = smaller_b
        if "activation" in model.attrs and model.attrs["activation"] in ["softmax", "logistic"]:
            # ensure little influence on the softmax/logistic activation
            larger_b[old_nO:] = NEG_VALUE
        layer.set_param("W", larger_W)
        layer.set_param("b", larger_b)
    layer.set_dim("nO", new_nO, force=True)
    model.set_dim("nO", new_nO, force=True)
    return model


@registry.architectures("spacy.TextCatEnsemble.v3")
def build_text_classifier_v3(
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
        cnn_output_layer = Linear(nO=nO, nI=width)
        cnn_model = (
            tok2vec
            >> list2ragged()
            >> attention_layer
            >> reduce_sum()
            >> residual(maxout_layer >> norm_layer >> Dropout(0.0))
            >> cnn_output_layer
        )
        cnn_model.attrs["activation"] = "linear"

        nO_double = nO * 2 if nO else None
        if exclusive_classes:
            output_layer = Softmax(nO=nO, nI=nO_double)
            model = (linear_model | cnn_model) >> output_layer
            model.attrs["activation"] = "softmax"
        else:
            output_layer = Linear(nO=nO, nI=nO_double)
            model = (linear_model | cnn_model) >> output_layer >> Logistic()
            model.attrs["activation"] = "logistic"
        model.set_ref("tok2vec", tok2vec)
    if model.has_dim("nO") is not False:
        model.set_dim("nO", nO)
    model.set_ref("output_layer", linear_model.get_ref("output_layer"))
    model.set_ref("attention_layer", attention_layer)
    model.set_ref("maxout_layer", maxout_layer)
    model.set_ref("norm_layer", norm_layer)
    model.attrs["multi_label"] = not exclusive_classes
    linear_output_layer = linear_model.get_ref("output_layer")
    model.attrs["resize_output"] = partial(
        _resize_ensemble,
        layer=output_layer,
        linear_model=linear_model,
        linear_input=linear_output_layer,
        cnn_model=cnn_model,
        cnn_input=cnn_output_layer,
    )
    model.init = init_ensemble_textcat
    return model


def _resize_ensemble(model, new_nO, layer, linear_model, linear_input, cnn_model, cnn_input):
    """ Resize an ensemble layer and its two input layer in-place"""
    if layer.has_dim("nO") is None:
        # the output layer had not been initialized/trained yet
        layer.set_dim("nO", new_nO)
        return model
    elif new_nO == layer.get_dim("nO"):
        # the dimensions didn't change
        return model

    # resize the two input layers and the new output layer
    _resize_bow(linear_model, new_nO, linear_input)
    _resize_layer(cnn_model, new_nO, cnn_input)
    return _resize_concatting_layer(model, new_nO, layer, input_layers=2)


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
