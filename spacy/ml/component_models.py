from thinc.layers import LayerNorm

from spacy import util
from spacy.ml.extract_ngrams import extract_ngrams

from ..attrs import ID, ORTH, NORM, PREFIX, SUFFIX, SHAPE
from ..errors import Errors
from ._character_embed import CharacterEmbed

from thinc.api import Model, Maxout, Linear, residual, reduce_mean, list2ragged
from thinc.api import PyTorchLSTM, add, MultiSoftmax, HashEmbed, StaticVectors
from thinc.api import expand_window, FeatureExtractor, SparseLinear, chain
from thinc.api import clone, concatenate, with_array, Softmax, Logistic, uniqued
from thinc.api import zero_init, glorot_uniform_init


def build_text_classifier(
    architecture,
    tok2vec,
    nr_class=1,
    exclusive_classes=None,
    ngram_size=1,
    no_output_layer=False,
):
    if nr_class == 1:
        exclusive_classes = False
    if exclusive_classes is None:
        raise ValueError(
            "TextCategorizer Model must specify 'exclusive_classes'. "
            "This setting determines whether the model will output "
            "scores that sum to 1 for each example. If only one class "
            "is true for each example, you should set exclusive_classes=True. "
            "For 'multi_label' classification, set exclusive_classes=False."
        )
    if architecture == "bow":
        return build_bow_text_classifier(
            nr_class, exclusive_classes, ngram_size, no_output_layer
        )
    elif architecture == "cnn":
        return build_simple_cnn_text_classifier(tok2vec, nr_class, exclusive_classes)
    else:
        raise ValueError("Unexpected textcat arch")


def build_simple_cnn_text_classifier(tok2vec, nr_class, exclusive_classes):
    """
    Build a simple CNN text classifier, given a token-to-vector model as inputs.
    If exclusive_classes=True, a softmax non-linearity is applied, so that the
    outputs sum to 1. If exclusive_classes=False, a logistic non-linearity
    is applied instead, so that outputs are in the range [0, 1].
    """
    with Model.define_operators({">>": chain}):
        if exclusive_classes:
            output_layer = Softmax(nO=nr_class, nI=tok2vec.get_dim("nO"))
        else:
            # TODO: experiment with init_w=zero_init
            output_layer = Linear(nO=nr_class, nI=tok2vec.get_dim("nO")) >> Logistic()
        model = tok2vec >> list2ragged() >> reduce_mean() >> output_layer
    model.set_ref("tok2vec", tok2vec)
    model.set_dim("nO", nr_class)
    return model


def build_bow_text_classifier(nr_class, exclusive_classes, ngram_size, no_output_layer):
    with Model.define_operators({">>": chain}):
        model = extract_ngrams(ngram_size, attr=ORTH) >> SparseLinear(nr_class)
        model.to_cpu()
        if not no_output_layer:
            output_layer = (
                Softmax(nO=nr_class) if exclusive_classes else Logistic(nO=nr_class)
            )
            output_layer.to_cpu()
            model = model >> output_layer
    model.set_dim("nO", nr_class)
    return model


def build_nel_encoder(
    entity_width, tok2vec, hidden_width=128, ner_types=None, pretrained_vectors=None
):
    with Model.define_operators({">>": chain, "**": clone}):
        model = (
            tok2vec
            >> list2ragged()
            >> reduce_mean()
            >> residual(Maxout(nO=hidden_width, nI=hidden_width, nP=2, dropout=0.0))
            >> Linear(nO=entity_width, nI=hidden_width)
        )
        model.initialize()
        model.set_ref("tok2vec", tok2vec)
        model.set_dim("nO", entity_width)
    return model


def masked_language_model(*args, **kwargs):
    raise NotImplementedError


def build_tagger_model(nr_class, tok2vec):
    token_vector_width = tok2vec.get_dim("nO")
    # TODO: glorot_uniform_init seems to work a bit better than zero_init here?!
    softmax = with_array(Softmax(nO=nr_class, nI=token_vector_width, init_W=zero_init))
    model = chain(tok2vec, softmax)
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("softmax", softmax)
    return model


def multi_task_model(n_tags, tok2vec=None, token_vector_width=96):
    model = chain(
        tok2vec,
        Maxout(nO=token_vector_width * 2, nI=token_vector_width, nP=3, dropout=0.0),
        LayerNorm(token_vector_width * 2),
        Softmax(nO=n_tags, nI=token_vector_width * 2),
    )
    return model


def cloze_multi_task_model(vocab, tok2vec):
    output_size = vocab.vectors.data.shape[1]
    output_layer = chain(
        Maxout(
            nO=output_size, nI=tok2vec.get_dim("nO"), nP=3, normalize=True, dropout=0.0
        ),
        Linear(nO=output_size, nI=output_size, init_W=zero_init),
    )
    model = chain(tok2vec, output_layer)
    model = masked_language_model(vocab, model)
    return model


def tensorizer(input_size=96, output_size=300):
    input_size = util.env_opt("token_vector_width", input_size)
    return Linear(output_size, input_size, init_W=zero_init)


def build_morphologizer_model(class_nums, pretrained_vectors, **cfg):
    embed_size = util.env_opt("embed_size", 7000)
    if "token_vector_width" in cfg:
        token_vector_width = cfg["token_vector_width"]
    else:
        token_vector_width = util.env_opt("token_vector_width", 128)
    char_embed = cfg.get("char_embed", True)
    with Model.define_operators({">>": chain, "+": add, "**": clone}):
        if "tok2vec" in cfg:
            tok2vec = cfg["tok2vec"]
        else:
            tok2vec = Tok2Vec(
                token_vector_width,
                embed_size,
                char_embed=char_embed,
                pretrained_vectors=pretrained_vectors,
            )
        softmax = with_array(MultiSoftmax(nOs=class_nums, nI=token_vector_width))
        model = tok2vec >> softmax
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("softmax", softmax)
    return model


def Tok2Vec(
    width,
    embed_size,
    pretrained_vectors=None,
    window_size=1,
    cnn_maxout_pieces=3,
    subword_features=True,
    char_embed=False,
    conv_depth=4,
    bilstm_depth=0,
):
    if char_embed:
        subword_features = False
    cols = [ID, NORM, PREFIX, SUFFIX, SHAPE, ORTH]
    with Model.define_operators({">>": chain, "|": concatenate, "**": clone}):
        norm = HashEmbed(nO=width, nV=embed_size, column=cols.index(NORM), dropout=0.0)
        if subword_features:
            prefix = HashEmbed(
                nO=width, nV=embed_size // 2, column=cols.index(PREFIX), dropout=0.0
            )
            suffix = HashEmbed(
                nO=width, nV=embed_size // 2, column=cols.index(SUFFIX), dropout=0.0
            )
            shape = HashEmbed(
                nO=width, nV=embed_size // 2, column=cols.index(SHAPE), dropout=0.0
            )
        else:
            prefix, suffix, shape = (None, None, None)
        if pretrained_vectors is not None:
            glove = StaticVectors(
                vectors=pretrained_vectors, nO=width, column=cols.index(ID), dropout=0.0
            )

            if subword_features:
                embed = uniqued(
                    (glove | norm | prefix | suffix | shape)
                    >> Maxout(
                        nO=width, nI=width * 5, nP=3, dropout=0.0, normalize=True
                    ),
                    column=cols.index(ORTH),
                )
            else:
                embed = uniqued(
                    (glove | norm)
                    >> Maxout(
                        nO=width, nI=width * 2, nP=3, dropout=0.0, normalize=True
                    ),
                    column=cols.index(ORTH),
                )
        elif subword_features:
            embed = uniqued(
                concatenate(norm, prefix, suffix, shape)
                >> Maxout(nO=width, nI=width * 4, nP=3, dropout=0.0, normalize=True),
                column=cols.index(ORTH),
            )
        elif char_embed:
            embed = CharacterEmbed(nM=64, nC=8) | FeatureExtractor(cols) >> with_array(
                norm
            )
            reduce_dimensions = Maxout(
                nO=width,
                nI=64 * 8 + width,
                nP=cnn_maxout_pieces,
                dropout=0.0,
                normalize=True,
            )
        else:
            embed = norm

        convolution = residual(
            expand_window(window_size=window_size)
            >> Maxout(
                nO=width,
                nI=width * 3,
                nP=cnn_maxout_pieces,
                dropout=0.0,
                normalize=True,
            )
        )
        if char_embed:
            tok2vec = embed >> with_array(
                reduce_dimensions >> convolution ** conv_depth, pad=conv_depth
            )
        else:
            tok2vec = FeatureExtractor(cols) >> with_array(
                embed >> convolution ** conv_depth, pad=conv_depth
            )

        if bilstm_depth >= 1:
            tok2vec = tok2vec >> PyTorchLSTM(
                nO=width, nI=width, depth=bilstm_depth, bi=True
            )
        # Work around thinc API limitations :(. TODO: Revise in Thinc 7
        tok2vec.set_dim("nO", width)
        tok2vec.set_ref("embed", embed)
    return tok2vec
