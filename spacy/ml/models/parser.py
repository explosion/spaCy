from pathlib import Path
from pydantic import StrictInt

from spacy import util
from spacy.util import registry
from spacy.errors import TempErrors
from spacy.ml._layers import PrecomputableAffine
from spacy.syntax._parser_model import ParserModel

from thinc.model import Model
from thinc.layers import chain, list2array, Linear
from thinc.initializers import zero_init
from thinc.backends import use_ops


def default_parser_config(tok2vec_config=None):
    from . import default_tok2vec_config

    if tok2vec_config is None:
        tok2vec_config = default_tok2vec_config()

    loc = Path(__file__).parent / "defaults" / "parser_defaults.cfg"
    parser_config = util.load_from_config(loc, create_objects=False)
    parser_config["model"]["tok2vec"] = tok2vec_config["model"]
    return parser_config


@registry.architectures.register("spacy.TransitionBasedParser.v1")
def create_tb_parser_model(
    tok2vec: Model,
    nr_feature_tokens: StrictInt = 3,
    hidden_width: StrictInt = 64,
    maxout_pieces: StrictInt = 3,
):
    token_vector_width = tok2vec.get_dim("nO")
    tok2vec = chain(tok2vec, list2array())
    tok2vec.set_dim("nO", token_vector_width)

    lower = PrecomputableAffine(
        hidden_width, nF=nr_feature_tokens, nI=tok2vec.get_dim("nO"), nP=maxout_pieces
    )
    lower.set_dim("nP", maxout_pieces)
    with use_ops("numpy"):
        # Initialize weights at zero, as it's a classification layer.
        upper = Linear(init_W=zero_init)
    return ParserModel(tok2vec, lower, upper)


def build_old_parser_model(tok2vec, nr_class, cfg):
    depth = util.env_opt("parser_hidden_depth", cfg.get("hidden_depth", 1))
    self_attn_depth = util.env_opt("self_attn_depth", cfg.get("self_attn_depth", 0))
    nr_feature_tokens = cfg.get("nr_feature_tokens")
    if depth not in (0, 1):
        raise ValueError(TempErrors.T004.format(value=depth))
    parser_maxout_pieces = util.env_opt(
        "parser_maxout_pieces", cfg.get("maxout_pieces", 2)
    )
    hidden_width = util.env_opt("hidden_width", cfg.get("hidden_width", 64))
    if depth == 0:
        hidden_width = nr_class
        parser_maxout_pieces = 1
    parser_tok2vec = chain(tok2vec, list2array())
    token_vector_width = tok2vec.get_dim("nO")
    parser_tok2vec.set_dim("nO", token_vector_width)

    lower = PrecomputableAffine(
        nO=hidden_width,
        nF=nr_feature_tokens,
        nI=token_vector_width,
        nP=parser_maxout_pieces,
    )
    lower.set_dim("nP", parser_maxout_pieces)
    if depth == 1:
        with use_ops("numpy"):
            upper = Linear(nO=nr_class, nI=hidden_width, init_W=zero_init)
    else:
        upper = None

    model = ParserModel(parser_tok2vec, lower, upper)
    return model
