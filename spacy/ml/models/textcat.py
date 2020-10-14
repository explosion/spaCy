from typing import Optional
from thinc.api import Model, reduce_mean, Linear, list2ragged, Logistic
from thinc.api import chain, concatenate, clone, Dropout, ParametricAttention
from thinc.api import SparseLinear, Softmax, softmax_activation, Maxout, reduce_sum
from thinc.api import HashEmbed, with_array, with_cpu, uniqued
from thinc.api import Relu, residual, expand_window

from ...attrs import ID, ORTH, PREFIX, SUFFIX, SHAPE, LOWER
from ...util import registry
from ..extract_ngrams import extract_ngrams
from ..staticvectors import StaticVectors
from ..featureextractor import FeatureExtractor


@registry.architectures.register("spacy.TextCatCNN.v1")
def build_simple_cnn_text_classifier(
    tok2vec: Model, exclusive_classes: bool, nO: Optional[int] = None
) -> Model:
    """
    Build a simple CNN text classifier, given a token-to-vector model as inputs.
    If exclusive_classes=True, a softmax non-linearity is applied, so that the
    outputs sum to 1. If exclusive_classes=False, a logistic non-linearity
    is applied instead, so that outputs are in the range [0, 1].
    """
    with Model.define_operators({">>": chain}):
        if exclusive_classes:
            output_layer = Softmax(nO=nO, nI=tok2vec.maybe_get_dim("nO"))
            model = tok2vec >> list2ragged() >> reduce_mean() >> output_layer
            model.set_ref("output_layer", output_layer)
        else:
            linear_layer = Linear(nO=nO, nI=tok2vec.maybe_get_dim("nO"))
            model = (
                tok2vec >> list2ragged() >> reduce_mean() >> linear_layer >> Logistic()
            )
            model.set_ref("output_layer", linear_layer)
    model.set_ref("tok2vec", tok2vec)
    model.set_dim("nO", nO)
    model.attrs["multi_label"] = not exclusive_classes
    return model


@registry.architectures.register("spacy.TextCatBOW.v1")
def build_bow_text_classifier(
    exclusive_classes: bool,
    ngram_size: int,
    no_output_layer: bool,
    nO: Optional[int] = None,
) -> Model:
    # Don't document this yet, I'm not sure it's right.
    with Model.define_operators({">>": chain}):
        sparse_linear = SparseLinear(nO)
        model = extract_ngrams(ngram_size, attr=ORTH) >> sparse_linear
        model = with_cpu(model, model.ops)
        if not no_output_layer:
            output_layer = softmax_activation() if exclusive_classes else Logistic()
            model = model >> with_cpu(output_layer, output_layer.ops)
    model.set_ref("output_layer", sparse_linear)
    model.attrs["multi_label"] = not exclusive_classes
    return model


@registry.architectures.register("spacy.TextCatEnsemble.v1")
def build_text_classifier(
    width: int,
    embed_size: int,
    pretrained_vectors: Optional[bool],
    exclusive_classes: bool,
    ngram_size: int,
    window_size: int,
    conv_depth: int,
    dropout: Optional[float],
    nO: Optional[int] = None,
) -> Model:
    # Don't document this yet, I'm not sure it's right.
    cols = [ORTH, LOWER, PREFIX, SUFFIX, SHAPE, ID]
    with Model.define_operators({">>": chain, "|": concatenate, "**": clone}):
        lower = HashEmbed(
            nO=width, nV=embed_size, column=cols.index(LOWER), dropout=dropout, seed=10
        )
        prefix = HashEmbed(
            nO=width // 2,
            nV=embed_size,
            column=cols.index(PREFIX),
            dropout=dropout,
            seed=11,
        )
        suffix = HashEmbed(
            nO=width // 2,
            nV=embed_size,
            column=cols.index(SUFFIX),
            dropout=dropout,
            seed=12,
        )
        shape = HashEmbed(
            nO=width // 2,
            nV=embed_size,
            column=cols.index(SHAPE),
            dropout=dropout,
            seed=13,
        )
        width_nI = sum(layer.get_dim("nO") for layer in [lower, prefix, suffix, shape])
        trained_vectors = FeatureExtractor(cols) >> with_array(
            uniqued(
                (lower | prefix | suffix | shape)
                >> Maxout(nO=width, nI=width_nI, normalize=True),
                column=cols.index(ORTH),
            )
        )
        if pretrained_vectors:
            static_vectors = StaticVectors(width)
            vector_layer = trained_vectors | static_vectors
            vectors_width = width * 2
        else:
            vector_layer = trained_vectors
            vectors_width = width
        tok2vec = vector_layer >> with_array(
            Maxout(width, vectors_width, normalize=True)
            >> residual(
                (
                    expand_window(window_size=window_size)
                    >> Maxout(
                        nO=width, nI=width * ((window_size * 2) + 1), normalize=True
                    )
                )
            )
            ** conv_depth,
            pad=conv_depth,
        )
        cnn_model = (
            tok2vec
            >> list2ragged()
            >> ParametricAttention(width)
            >> reduce_sum()
            >> residual(Maxout(nO=width, nI=width))
            >> Linear(nO=nO, nI=width)
            >> Dropout(0.0)
        )

        linear_model = build_bow_text_classifier(
            nO=nO,
            ngram_size=ngram_size,
            exclusive_classes=exclusive_classes,
            no_output_layer=False,
        )
        nO_double = nO * 2 if nO else None
        if exclusive_classes:
            output_layer = Softmax(nO=nO, nI=nO_double)
        else:
            output_layer = Linear(nO=nO, nI=nO_double) >> Dropout(0.0) >> Logistic()
        model = (linear_model | cnn_model) >> output_layer
        model.set_ref("tok2vec", tok2vec)
    if model.has_dim("nO") is not False:
        model.set_dim("nO", nO)
    model.set_ref("output_layer", linear_model.get_ref("output_layer"))
    model.attrs["multi_label"] = not exclusive_classes
    return model


@registry.architectures.register("spacy.TextCatLowData.v1")
def build_text_classifier_lowdata(
    width: int,
    pretrained_vectors: Optional[bool],
    dropout: Optional[float],
    nO: Optional[int] = None,
) -> Model:
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
