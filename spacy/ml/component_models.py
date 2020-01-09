from . import common
from ..errors import Errors

from thinc.model import Model
from thinc.layers import Maxout, Linear, Residual, MeanPool, list2ragged, Residual, PyTorchBiLSTM
from thinc.layers import HashEmbed, StaticVectors, ExtractWindow, LayerNorm, FeatureExtractor
from thinc.layers import chain, clone, concatenate, uniqued, with_list2array, Softmax
from thinc.initializers import xavier_uniform_init, zero_init

from ..attrs import ID, ORTH, NORM, PREFIX, SUFFIX, SHAPE


def build_text_classifier(*args, **kwargs):
    raise NotImplementedError


def build_simple_cnn_text_classifier(*args, **kwargs):
    raise NotImplementedError


def build_bow_text_classifier(*args, **kwargs):
    raise NotImplementedError


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

        # TODO: Maxout & Linear defaults are xavier_uniform_init - experiment ?
        weight_init = zero_init

        model = (
            nel_tok2vec
            >> list2ragged()
            >> MeanPool()
            >> Residual(
                Maxout(nO=hidden_width, nI=hidden_width, nP=3, init_W=weight_init)
            )
            >> Linear(nO=context_width, nI=hidden_width, init_W=weight_init)
        )
        model.initialize()

        model.set_ref("tok2vec", nel_tok2vec)
        model.set_dim("nO", context_width)
    return model


def masked_language_model(*args, **kwargs):
    raise NotImplementedError


def build_tagger_model(nr_class, tok2vec):
    token_vector_width = tok2vec.get_dim("nO")
    with Model.define_operators({">>": chain}):
        softmax = with_list2array(Softmax(nr_class, token_vector_width))
        model = tok2vec >> softmax
    model.set_dim("nI", None)
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("softmax", softmax)
    return model


def build_morphologizer_model(*args, **kwargs):
    raise NotImplementedError


def Tok2Vec(
    width,
    pretrained_vectors,
    embed_size,
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
        norm = HashEmbed(width, embed_size, column=cols.index(NORM))
        if subword_features:
            prefix = HashEmbed(
                width, embed_size // 2, column=cols.index(PREFIX)
            )
            suffix = HashEmbed(
                width, embed_size // 2, column=cols.index(SUFFIX)
            )
            shape = HashEmbed(
                width, embed_size // 2, column=cols.index(SHAPE)
            )
        else:
            prefix, suffix, shape = (None, None, None)
        if pretrained_vectors is not None:
            glove = StaticVectors(pretrained_vectors, width, column=cols.index(ID))

            if subword_features:
                embed = uniqued(
                    (glove | norm | prefix | suffix | shape)
                    >> Maxout(nO=width, nI=width * 5, nP=3) >> LayerNorm(nO=width),
                    column=cols.index(ORTH),
                )
            else:
                embed = uniqued(
                    (glove | norm) >> Maxout(nO=width, nI=width * 2, nP=3) >> LayerNorm(nO=width),
                    column=cols.index(ORTH),
                )
        elif subword_features:
            embed = uniqued(
                (norm | prefix | suffix | shape)
                >> Maxout(nO=width, nI=width * 4, nP=3) >> LayerNorm(nO=width),
                column=cols.index(ORTH),
            )
        elif char_embed:
            embed = CharacterEmbed(nM=64, nC=8) | FeatureExtractor(cols) >> with_list2array(norm)
            reduce_dimensions = Maxout(nO=width, nI=64 * 8 + width, nP=cnn_maxout_pieces) >> LayerNorm(nO=width)
        else:
            embed = norm

        convolution = Residual(
            ExtractWindow(window_size=window_size)
            >> Maxout(nO=width, nI=width * 3, nP=cnn_maxout_pieces)
            >> LayerNorm(nO=width)
        )
        if char_embed:
            tok2vec = embed >> with_list2array(
                reduce_dimensions >> convolution ** conv_depth, pad=conv_depth
            )
        else:
            tok2vec = FeatureExtractor(cols) >> with_list2array(
                embed >> convolution ** conv_depth, pad=conv_depth
            )

        if bilstm_depth >= 1:
            tok2vec = tok2vec >> PyTorchBiLSTM(width, width, bilstm_depth)
        # Work around thinc API limitations :(. TODO: Revise in Thinc 7
        tok2vec.set_dim("nO", width)
        tok2vec.set_ref("embed", embed)
        tok2vec.initialize()
    return tok2vec


get_cossim_loss = None
PrecomputableAffine = None
flatten = None
