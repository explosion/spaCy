# cython: infer_types=True, profile=True, binding=True
from typing import Optional, Iterable
from thinc.api import CosineDistance, to_categorical, get_array_module, Model

from ..syntax.nn_parser cimport Parser
from ..syntax.arc_eager cimport ArcEager

from .functions import merge_subtokens
from ..language import Language
from ..syntax import nonproj
from ..util import load_config_from_str


default_model_config = """
[model]
@architectures = "spacy.TransitionBasedParser.v1"
nr_feature_tokens = 8
hidden_width = 64
maxout_pieces = 2

[model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v1"
pretrained_vectors = null
width = 96
depth = 4
embed_size = 2000
window_size = 1
maxout_pieces = 3
subword_features = true
dropout = null
"""
DEFAULT_PARSER_MODEL = load_config_from_str(default_model_config, create_objects=False)["model"]


@Language.factory(
    "parser",
    assigns=["token.dep", "token.is_sent_start", "doc.sents"],
    default_config={
        "moves": None,
        "update_with_oracle_cut_size": 100,
        "multitasks": [],
        "learn_tokens": False,
        "min_action_freq": 30,
        "model": DEFAULT_PARSER_MODEL,
    }
)
def make_parser(
    nlp: Language,
    name: str,
    model: Model,
    moves: Optional[list],
    update_with_oracle_cut_size: int,
    multitasks: Iterable,
    learn_tokens: bool,
    min_action_freq: int
):
    return DependencyParser(
        nlp.vocab,
        model,
        name,
        moves=moves,
        update_with_oracle_cut_size=update_with_oracle_cut_size,
        multitasks=multitasks,
        learn_tokens=learn_tokens,
        min_action_freq=min_action_freq
    )


cdef class DependencyParser(Parser):
    """Pipeline component for dependency parsing.

    DOCS: https://spacy.io/api/dependencyparser
    """
    # cdef classes can't have decorators, so we're defining this here
    TransitionSystem = ArcEager

    @property
    def postprocesses(self):
        output = [nonproj.deprojectivize]
        if self.cfg.get("learn_tokens") is True:
            output.append(merge_subtokens)
        return tuple(output)

    def add_multitask_objective(self, mt_component):
        self._multitasks.append(mt_component)

    def init_multitask_objectives(self, get_examples, pipeline, sgd=None, **cfg):
        # TODO: transfer self.model.get_ref("tok2vec") to the multitask's model ?
        for labeller in self._multitasks:
            labeller.model.set_dim("nO", len(self.labels))
            if labeller.model.has_ref("output_layer"):
                labeller.model.get_ref("output_layer").set_dim("nO", len(self.labels))
            labeller.begin_training(get_examples, pipeline=pipeline, sgd=sgd)

    @property
    def labels(self):
        labels = set()
        # Get the labels from the model by looking at the available moves
        for move in self.move_names:
            if "-" in move:
                label = move.split("-")[1]
                if "||" in label:
                    label = label.split("||")[1]
                labels.add(label)
        return tuple(sorted(labels))
