from typing import Optional
from thinc.api import Model, chain, list2array, Linear, zero_init, use_ops

from ...util import registry
from .._precomputable_affine import PrecomputableAffine
from ..tb_framework import TransitionModel


@registry.architectures.register("spacy.TransitionBasedParser.v1")
def build_tb_parser_model(
    tok2vec: Model,
    nr_feature_tokens: int,
    hidden_width: int,
    maxout_pieces: int,
    use_upper: bool = True,
    nO: Optional[int] = None,
) -> Model:
    t2v_width = tok2vec.get_dim("nO") if tok2vec.has_dim("nO") else None
    tok2vec = chain(tok2vec, list2array(), Linear(hidden_width, t2v_width),)
    tok2vec.set_dim("nO", hidden_width)
    lower = PrecomputableAffine(
        nO=hidden_width if use_upper else nO,
        nF=nr_feature_tokens,
        nI=tok2vec.get_dim("nO"),
        nP=maxout_pieces,
    )
    if use_upper:
        with use_ops("numpy"):
            # Initialize weights at zero, as it's a classification layer.
            upper = Linear(nO=nO, init_W=zero_init)
    else:
        upper = None
    return TransitionModel(tok2vec, lower, upper)
