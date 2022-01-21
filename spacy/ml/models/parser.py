from typing import Optional, List, Tuple, Any
from thinc.types import Floats2d
from thinc.api import Model

from ...errors import Errors
from ...compat import Literal
from ...util import registry
from ..tb_framework import TransitionModel
from ...tokens.doc import Doc

TransitionSystem = Any  # TODO
State = Any  # TODO


@registry.architectures.register("spacy.TransitionBasedParser.v3")
def transition_parser_v3(
    tok2vec: Model[List[Doc], List[Floats2d]],
    state_type: Literal["parser", "ner"],
    extra_state_tokens: bool,
    hidden_width: int,
    maxout_pieces: int,
    nO: Optional[int] = None,
) -> Model:
    return build_tb_parser_model(
        tok2vec,
        state_type,
        extra_state_tokens,
        hidden_width,
        maxout_pieces,
        nO=nO,
    )


def build_tb_parser_model(
    tok2vec: Model[List[Doc], List[Floats2d]],
    state_type: Literal["parser", "ner"],
    extra_state_tokens: bool,
    hidden_width: int,
    maxout_pieces: int,
    nO: Optional[int] = None,
) -> Model:
    """
    Build a transition-based parser model. Can apply to NER or dependency-parsing.

    Transition-based parsing is an approach to structured prediction where the
    task of predicting the structure is mapped to a series of state transitions.
    You might find this tutorial helpful as background:
    https://explosion.ai/blog/parsing-english-in-python

    The neural network state prediction model consists of either two or three
    subnetworks:

    * tok2vec: Map each token into a vector representations. This subnetwork
        is run once for each batch.
    * lower: Construct a feature-specific vector for each (token, feature) pair.
        This is also run once for each batch. Constructing the state
        representation is then simply a matter of summing the component features
        and applying the non-linearity.
    * upper (optional): A feed-forward network that predicts scores from the
        state representation. If not present, the output from the lower model is
        used as action scores directly.

    tok2vec (Model[List[Doc], List[Floats2d]]):
        Subnetwork to map tokens into vector representations.
    state_type (str):
        String value denoting the type of parser model: "parser" or "ner"
    extra_state_tokens (bool): Whether or not to use additional tokens in the context
        to construct the state vector. Defaults to `False`, which means 3 and 8
        for the NER and parser respectively. When set to `True`, this would become 6
        feature sets (for the NER) or 13 (for the parser).
    hidden_width (int): The width of the hidden layer.
    maxout_pieces (int): How many pieces to use in the state prediction layer.
        Recommended values are 1, 2 or 3.
    nO (int or None): The number of actions the model will predict between.
        Usually inferred from data at the beginning of training, or loaded from
        disk.
    """
    if state_type == "parser":
        nr_feature_tokens = 13 if extra_state_tokens else 8
    elif state_type == "ner":
        nr_feature_tokens = 6 if extra_state_tokens else 3
    else:
        raise ValueError(Errors.E917.format(value=state_type))
    return TransitionModel(
        tok2vec=tok2vec,
        state_tokens=nr_feature_tokens,
        hidden_width=hidden_width,
        maxout_pieces=maxout_pieces,
        nO=nO,
        unseen_classes=set(),
    )
