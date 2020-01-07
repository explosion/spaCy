from ..errors import Errors

from thinc.model import Model
from thinc.layers import Maxout, Linear, Residual, MeanPool, list2ragged
from thinc.layers import chain, clone
from thinc.initializers import xavier_uniform_init, zero_init


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
        # context encoder
        tok2vec = Tok2Vec(
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
            tok2vec
            >> list2ragged
            >> MeanPool
            >> Residual(Maxout(nO=hidden_width, nI=hidden_width, nP=3, init_W=weight_init))
            >> Linear(nO=context_width, nI=hidden_width, init_W=weight_init)
        )

        model.tok2vec = tok2vec
        model.nO = context_width
    return model


def masked_language_model(*args, **kwargs):
    raise NotImplementedError


def build_tagger_model(*args, **kwargs):
    raise NotImplementedError


def build_morphologizer_model(*args, **kwargs):
    raise NotImplementedError


def Tok2Vec(*args, **kwargs):
    raise NotImplementedError


get_cossim_loss = None
PrecomputableAffine = None
flatten = None
