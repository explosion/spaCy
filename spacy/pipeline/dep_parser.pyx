# cython: infer_types=True, binding=True
import importlib
import sys
from collections import defaultdict
from typing import Callable, Optional

from thinc.api import Config, Model

from ._parser_internals.transition_system import TransitionSystem

from ._parser_internals.arc_eager cimport ArcEager
from .transition_parser cimport Parser

from ..language import Language
from ..scorer import Scorer
from ..training import remove_bilu_prefix
from ..util import registry
from ._parser_internals import nonproj
from ._parser_internals.nonproj import DELIMITER
from .functions import merge_subtokens

default_model_config = """
[model]
@architectures = "spacy.TransitionBasedParser.v2"
state_type = "parser"
extra_state_tokens = false
hidden_width = 64
maxout_pieces = 2
use_upper = true

[model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v2"
pretrained_vectors = null
width = 96
depth = 4
embed_size = 2000
window_size = 1
maxout_pieces = 3
subword_features = true
"""
DEFAULT_PARSER_MODEL = Config().from_str(default_model_config)["model"]


def parser_score(examples, **kwargs):
    """Score a batch of examples.

    examples (Iterable[Example]): The examples to score.
    RETURNS (Dict[str, Any]): The scores, produced by Scorer.score_spans
        and Scorer.score_deps.

    DOCS: https://spacy.io/api/dependencyparser#score
    """
    def has_sents(doc):
        return doc.has_annotation("SENT_START")

    def dep_getter(token, attr):
        dep = getattr(token, attr)
        dep = token.vocab.strings.as_string(dep).lower()
        return dep
    results = {}
    results.update(Scorer.score_spans(examples, "sents", has_annotation=has_sents, **kwargs))
    kwargs.setdefault("getter", dep_getter)
    kwargs.setdefault("ignore_labels", ("p", "punct"))
    results.update(Scorer.score_deps(examples, "dep", **kwargs))
    del results["sents_per_type"]
    return results


def make_parser_scorer():
    return parser_score


cdef class DependencyParser(Parser):
    """Pipeline component for dependency parsing.

    DOCS: https://spacy.io/api/dependencyparser
    """
    TransitionSystem = ArcEager

    def __init__(
        self,
        vocab,
        model,
        name="parser",
        moves=None,
        *,
        update_with_oracle_cut_size=100,
        min_action_freq=30,
        learn_tokens=False,
        beam_width=1,
        beam_density=0.0,
        beam_update_prob=0.0,
        multitasks=tuple(),
        incorrect_spans_key=None,
        scorer=parser_score,
    ):
        """Create a DependencyParser.
        """
        super().__init__(
            vocab,
            model,
            name,
            moves,
            update_with_oracle_cut_size=update_with_oracle_cut_size,
            min_action_freq=min_action_freq,
            learn_tokens=learn_tokens,
            beam_width=beam_width,
            beam_density=beam_density,
            beam_update_prob=beam_update_prob,
            multitasks=multitasks,
            incorrect_spans_key=incorrect_spans_key,
            scorer=scorer,
        )

    @property
    def postprocesses(self):
        output = [nonproj.deprojectivize]
        if self.cfg.get("learn_tokens") is True:
            output.append(merge_subtokens)
        return tuple(output)

    def add_multitask_objective(self, mt_component):
        self._multitasks.append(mt_component)

    def init_multitask_objectives(self, get_examples, nlp=None, **cfg):
        # TODO: transfer self.model.get_ref("tok2vec") to the multitask's model ?
        for labeller in self._multitasks:
            labeller.model.set_dim("nO", len(self.labels))
            if labeller.model.has_ref("output_layer"):
                labeller.model.get_ref("output_layer").set_dim("nO", len(self.labels))
            labeller.initialize(get_examples, nlp=nlp)

    @property
    def labels(self):
        labels = set()
        # Get the labels from the model by looking at the available moves
        for move in self.move_names:
            if "-" in move:
                label = remove_bilu_prefix(move)
                if DELIMITER in label:
                    label = label.split(DELIMITER)[1]
                labels.add(label)
        return tuple(sorted(labels))

    def scored_parses(self, beams):
        """Return two dictionaries with scores for each beam/doc that was processed:
        one containing (i, head) keys, and another containing (i, label) keys.
        """
        head_scores = []
        label_scores = []
        for beam in beams:
            score_head_dict = defaultdict(float)
            score_label_dict = defaultdict(float)
            for score, parses in self.moves.get_beam_parses(beam):
                for head, i, label in parses:
                    score_head_dict[(i, head)] += score
                    score_label_dict[(i, label)] += score
            head_scores.append(score_head_dict)
            label_scores.append(score_label_dict)
        return head_scores, label_scores

    def _ensure_labels_are_added(self, docs):
        # This gives the parser a chance to add labels it's missing for a batch
        # of documents. However, this isn't desirable for the dependency parser,
        # because we instead have a label frequency cut-off and back off rare
        # labels to 'dep'.
        pass


# Setup backwards compatibility hook for factories
def __getattr__(name):
    if name == "make_parser":
        module = importlib.import_module("spacy.pipeline.factories")
        return module.make_parser
    elif name == "make_beam_parser":
        module = importlib.import_module("spacy.pipeline.factories")
        return module.make_beam_parser
    raise AttributeError(f"module {__name__} has no attribute {name}")
