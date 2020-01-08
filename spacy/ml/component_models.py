from . import tok2vec, common
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

        model.set_ref("tok2vec", nel_tok2vec)
        model.set_dim("nO", context_width)
    return model


def masked_language_model(*args, **kwargs):
    raise NotImplementedError


def build_tagger_model(*args, **kwargs):
    raise NotImplementedError


def build_morphologizer_model(*args, **kwargs):
    raise NotImplementedError


def Tok2Vec(
    width,
    pretrained_vectors,
    conv_depth,
    bilstm_depth,
    embed_size,
    window_size=1,
    cnn_maxout_pieces=3,
    subword_features=True,
    char_embed=False,
):
    cols = ["ID", "NORM", "PREFIX", "SUFFIX", "SHAPE", "ORTH"]

    doc2feats_cfg = {"arch": "spacy.Doc2Feats.v1", "config": {"columns": cols}}
    if char_embed:
        embed_cfg = {
            "arch": "spacy.CharacterEmbed.v1",
            "config": {
                "width": 64,
                "chars": 6,
                "@mix": {
                    "arch": "spacy.LayerNormalizedMaxout.v1",
                    "config": {"width": width, "pieces": 3},
                },
                "@embed_features": None,
            },
        }
    else:
        embed_cfg = {
            "arch": "spacy.MultiHashEmbed.v1",
            "config": {
                "width": width,
                "rows": embed_size,
                "columns": cols,
                "use_subwords": subword_features,
                "@pretrained_vectors": None,
                "@mix": {
                    "arch": "spacy.LayerNormalizedMaxout.v1",
                    "config": {"width": width, "pieces": 3},
                },
            },
        }
        if pretrained_vectors:
            embed_cfg["config"]["@pretrained_vectors"] = {
                "arch": "spacy.PretrainedVectors.v1",
                "config": {
                    "vectors_name": pretrained_vectors,
                    "width": width,
                    "column": cols.index("ID"),
                },
            }
    if cnn_maxout_pieces >= 2:
        cnn_cfg = {
            "arch": "spacy.MaxoutWindowEncoder.v1",
            "config": {
                "width": width,
                "window_size": window_size,
                "pieces": cnn_maxout_pieces,
                "depth": conv_depth,
            },
        }
    else:
        cnn_cfg = {
            "arch": "spacy.MishWindowEncoder.v1",
            "config": {"width": width, "window_size": window_size, "depth": conv_depth},
        }
    bilstm_cfg = {
        "arch": "spacy.TorchBiLSTMEncoder.v1",
        "config": {"width": width, "depth": bilstm_depth},
    }
    if conv_depth == 0 and bilstm_depth == 0:
        encode_cfg = {}
    elif conv_depth >= 1 and bilstm_depth >= 1:
        encode_cfg = {
            "arch": "thinc.FeedForward.v1",
            "config": {"children": [cnn_cfg, bilstm_cfg]},
        }
    elif conv_depth >= 1:
        encode_cfg = cnn_cfg
    else:
        encode_cfg = bilstm_cfg
    config = {"@doc2feats": doc2feats_cfg, "@embed": embed_cfg, "@encode": encode_cfg}
    return tok2vec.Tok2Vec(config)


get_cossim_loss = None
PrecomputableAffine = None
flatten = None
