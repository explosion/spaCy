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


def default_parser_config():
    loc = Path(__file__).parent / "defaults" / "parser_defaults.cfg"
    return util.load_from_config(loc, create_objects=False)


def default_ner_config():
    loc = Path(__file__).parent / "defaults" / "ner_defaults.cfg"
    return util.load_from_config(loc, create_objects=False)


@registry.architectures.register("spacy.TransitionBasedParser.v1")
def build_tb_parser_model(
    tok2vec: Model,
    nr_class,
    nr_feature_tokens: StrictInt,
    hidden_width: StrictInt,
    maxout_pieces: StrictInt,
):
    token_vector_width = tok2vec.get_dim("nO")
    tok2vec = chain(tok2vec, list2array())
    tok2vec.set_dim("nO", token_vector_width)

    lower = PrecomputableAffine(
        nO=hidden_width,
        nF=nr_feature_tokens,
        nI=tok2vec.get_dim("nO"),
        nP=maxout_pieces,
    )
    lower.set_dim("nP", maxout_pieces)
    with use_ops("numpy"):
        # Initialize weights at zero, as it's a classification layer.
        upper = Linear(nO=nr_class, init_W=zero_init)
    return ParserModel(tok2vec, lower, upper)
