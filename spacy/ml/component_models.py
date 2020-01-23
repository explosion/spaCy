from spacy import util
from spacy.ml.extract_ngrams import extract_ngrams

from ..errors import Errors
from ._character_embed import CharacterEmbed

from thinc.api import Model, Maxout, Linear, residual, reduce_mean, list2ragged
from thinc.api import PyTorchLSTM, add, MultiSoftmax, HashEmbed, StaticVectors
from thinc.api import expand_window, FeatureExtractor, SparseLinear, chain
from thinc.api import clone, concatenate, with_array, Softmax, Logistic, uniqued
from thinc.api import zero_init, glorot_uniform_init

from ..attrs import ID, ORTH, NORM, PREFIX, SUFFIX, SHAPE


def build_text_classifier(arch, config):
    if arch == "cnn":
        return build_simple_cnn_text_classifier(**config)
    elif arch == "bow":
        return build_bow_text_classifier(**config)
    else:
        raise ValueError("Unexpected textcat arch")


def build_simple_cnn_text_classifier(tok2vec, nr_class, exclusive_classes=False, **cfg):
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
            output_layer = (
                Linear(nO=nr_class, nI=tok2vec.get_dim("nO"), init_W=zero_init)
                >> Logistic()
            )
        model = tok2vec >> list2ragged() >> reduce_mean() >> output_layer
    model.set_ref("tok2vec", tok2vec)
    model.set_dim("nO", nr_class)
    return model


def build_bow_text_classifier(
    nr_class, ngram_size=1, exclusive_classes=False, no_output_layer=False, **cfg
):
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


def build_nel_encoder(embed_width, hidden_width, ner_types, **cfg):
    if "entity_width" not in cfg:
        raise ValueError(Errors.E144.format(param="entity_width"))

    conv_depth = cfg.get("conv_depth", 2)
    cnn_maxout_pieces = cfg.get("cnn_maxout_pieces", 3)
    pretrained_vectors = cfg.get("pretrained_vectors", None)
    context_width = cfg.get("entity_width")

    with Model.define_operators({">>": chain, "**": clone}):
        nel_tok2vec = Tok2Vec(
            width=hidden_width,
            embed_size=embed_width,
            pretrained_vectors=pretrained_vectors,
            cnn_maxout_pieces=cnn_maxout_pieces,
            subword_features=True,
            conv_depth=conv_depth,
            bilstm_depth=0,
        )

        model = (
            nel_tok2vec
            >> list2ragged()
            >> reduce_mean()
            >> residual(Maxout(nO=hidden_width, nI=hidden_width, nP=2, dropout=0.0))
            >> Linear(nO=context_width, nI=hidden_width)
        )
        model.initialize()

        model.set_ref("tok2vec", nel_tok2vec)
        model.set_dim("nO", context_width)
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


def build_morphologizer_model(class_nums, **cfg):
    embed_size = util.env_opt("embed_size", 7000)
    if "token_vector_width" in cfg:
        token_vector_width = cfg["token_vector_width"]
    else:
        token_vector_width = util.env_opt("token_vector_width", 128)
    pretrained_vectors = cfg.get("pretrained_vectors")
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
        norm = HashEmbed(nO=width, nV=embed_size, column=cols.index(NORM))
        if subword_features:
            prefix = HashEmbed(nO=width, nV=embed_size // 2, column=cols.index(PREFIX))
            suffix = HashEmbed(nO=width, nV=embed_size // 2, column=cols.index(SUFFIX))
            shape = HashEmbed(nO=width, nV=embed_size // 2, column=cols.index(SHAPE))
        else:
            prefix, suffix, shape = (None, None, None)
        if pretrained_vectors is not None:
            glove = StaticVectors(pretrained_vectors, width, column=cols.index(ID))

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
            print("charembed", cnn_maxout_pieces)
            reduce_dimensions = Maxout(
                nO=width,
                nI=64 * 8 + width,
                nP=cnn_maxout_pieces,
                dropout=0.0,
                normalize=True,
            )
        else:
            embed = norm

        print("convolution", cnn_maxout_pieces)
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
