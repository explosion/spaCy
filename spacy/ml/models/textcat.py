from thinc.api import Model, reduce_mean, Linear, list2ragged, Logistic, ParametricAttention
from thinc.api import chain, add, concatenate, clone, zero_init, Dropout
from thinc.api import SparseLinear, Softmax, Maxout, reduce_sum, Relu, residual, expand_window
from thinc.api import HashEmbed, with_flatten, with_ragged, with_array, list2array, uniqued, FeatureExtractor

from ..spacy_vectors import SpacyVectors
from ... import util
from ...attrs import ID, ORTH, NORM, PREFIX, SUFFIX, SHAPE, LOWER
from ...util import registry
from ..extract_ngrams import extract_ngrams


@registry.architectures.register("spacy.TextCatCNN.v1")
def build_simple_cnn_text_classifier(tok2vec, exclusive_classes, nO=None):
    """
    Build a simple CNN text classifier, given a token-to-vector model as inputs.
    If exclusive_classes=True, a softmax non-linearity is applied, so that the
    outputs sum to 1. If exclusive_classes=False, a logistic non-linearity
    is applied instead, so that outputs are in the range [0, 1].
    """
    with Model.define_operators({">>": chain}):
        if exclusive_classes:
            output_layer = Softmax(nO=nO, nI=tok2vec.get_dim("nO"))
            model = tok2vec >> list2ragged() >> reduce_mean() >> output_layer
            model.set_ref("output_layer", output_layer)
        else:
            # TODO: experiment with init_w=zero_init
            linear_layer = Linear(nO=nO, nI=tok2vec.get_dim("nO"))
            model = (
                tok2vec >> list2ragged() >> reduce_mean() >> linear_layer >> Logistic()
            )
            model.set_ref("output_layer", linear_layer)
    model.set_ref("tok2vec", tok2vec)
    model.set_dim("nO", nO)
    return model


@registry.architectures.register("spacy.TextCatBOW.v1")
def build_bow_text_classifier(exclusive_classes, ngram_size, no_output_layer, nO=None):
    # Note: original defaults were ngram_size=1 and no_output_layer=False
    with Model.define_operators({">>": chain}):
        model = extract_ngrams(ngram_size, attr=ORTH) >> SparseLinear(nO)
        model.to_cpu()
        if not no_output_layer:
            output_layer = Softmax(nO) if exclusive_classes else Logistic()
            output_layer.to_cpu()
            model = model >> output_layer
            model.set_ref("output_layer", output_layer)
    return model


@registry.architectures.register("spacy.TextCat.v1")
def build_text_classifier(width, embed_size, pretrained_vectors, exclusive_classes, ngram_size,
                          window_size, conv_depth, nO=None):
    # Note: original defaults were window_size=1, ngram_size=1
    cols = [ORTH, LOWER, PREFIX, SUFFIX, SHAPE, ID]
    with Model.define_operators({">>": chain, "|": concatenate, "**": clone}):
        lower = HashEmbed(nO=width, nV=embed_size, column=cols.index(LOWER))
        prefix = HashEmbed(nO=width // 2, nV=embed_size, column=cols.index(PREFIX))
        suffix = HashEmbed(nO=width // 2, nV=embed_size, column=cols.index(SUFFIX))
        shape = HashEmbed(nO=width // 2, nV=embed_size, column=cols.index(SHAPE))

        trained_vectors = FeatureExtractor(cols) >> with_array(
            uniqued(
                (lower | prefix | suffix | shape)
                >> Maxout(width, width + (width // 2) * 3, normalize=True),
                column=0,
            )
        )

        if pretrained_vectors:
            nlp = util.load_model(pretrained_vectors)
            vectors = nlp.vocab.vectors
            vector_dim = vectors.data.shape[1]

            static_vectors = SpacyVectors(vectors) >> with_array(
                Linear(width, vector_dim)
            )
            vector_layer = trained_vectors | static_vectors
            vectors_width = width * 2
        else:
            vector_layer = trained_vectors
            vectors_width = width
        tok2vec = vector_layer >> with_array(
            Maxout(width, vectors_width, normalize=True)
            >> residual((expand_window(window_size=window_size) >> Maxout(width, width * 3, normalize=True))) ** conv_depth,
            pad=conv_depth,
        )
        cnn_model = (
                tok2vec
                >> list2ragged()
                >> ParametricAttention(width)
                >> reduce_sum()
                >> residual(Maxout(nO=width, nI=width, init_W=zero_init))
                >> Linear(nO=nO, nI=width, init_W=zero_init)
                >> Dropout(0.0)
        )

        linear_model = build_bow_text_classifier(
            nO=nO, ngram_size=ngram_size, exclusive_classes=False, no_output_layer=False
        )
        nO_double = nO*2 if nO else None
        if exclusive_classes:
            output_layer = Softmax(nO=nO, nI=nO_double)
        else:
            output_layer = (
                    Linear(nO=nO, nI=nO_double, init_W=zero_init) >> Dropout(0.0) >> Logistic()
            )
        model = (linear_model | cnn_model) >> output_layer
        # model.set_ref("tok2vec", chain(tok2vec, list2array()))
        model.set_ref("tok2vec", tok2vec)

    model.set_dim("nO", nO)
    return model


@registry.architectures.register("spacy.TextCatLowData.v1")
def build_text_classifier_lowdata(width, pretrained_vectors, nO=None):
    nlp = util.load_model(pretrained_vectors)
    vectors = nlp.vocab.vectors
    vector_dim = vectors.data.shape[1]

    # Note, before v.3, this was the default if setting "low_data" or "pretrained_dims"
    with Model.define_operators({">>": chain, "+": add, "|": concatenate, "**": clone}):
        model = (
            SpacyVectors(vectors)
            >> list2ragged()
            >> with_ragged(0, Linear(width, vector_dim))
            >> ParametricAttention(width)
            >> reduce_sum()
            >> residual(Relu(width, width)) ** 2
            >> Linear(nO, width, init_W=zero_init)
            >> Dropout(0.0)
            >> Logistic()
        )
    return model
