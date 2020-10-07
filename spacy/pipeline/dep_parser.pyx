# cython: infer_types=True, profile=True, binding=True
from typing import Optional, Iterable
from thinc.api import Model, Config

from .transition_parser cimport Parser
from ._parser_internals.arc_eager cimport ArcEager

from .functions import merge_subtokens
from ..language import Language
from ._parser_internals import nonproj
from ..scorer import Scorer
from ..training import validate_examples


default_model_config = """
[model]
@architectures = "spacy.TransitionBasedParser.v1"
state_type = "parser"
extra_state_tokens = false
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
"""
DEFAULT_PARSER_MODEL = Config().from_str(default_model_config)["model"]


@Language.factory(
    "parser",
    assigns=["token.dep", "token.head", "token.is_sent_start", "doc.sents"],
    default_config={
        "moves": None,
        "update_with_oracle_cut_size": 100,
        "learn_tokens": False,
        "min_action_freq": 30,
        "model": DEFAULT_PARSER_MODEL,
    },
    default_score_weights={
        "dep_uas": 0.5,
        "dep_las": 0.5,
        "dep_las_per_type": None,
        "sents_p": None,
        "sents_r": None,
        "sents_f": 0.0,
    },
)
def make_parser(
    nlp: Language,
    name: str,
    model: Model,
    moves: Optional[list],
    update_with_oracle_cut_size: int,
    learn_tokens: bool,
    min_action_freq: int
):
    """Create a transition-based DependencyParser component. The dependency parser
    jointly learns sentence segmentation and labelled dependency parsing, and can
    optionally learn to merge tokens that had been over-segmented by the tokenizer.

    The parser uses a variant of the non-monotonic arc-eager transition-system
    described by Honnibal and Johnson (2014), with the addition of a "break"
    transition to perform the sentence segmentation. Nivre's pseudo-projective
    dependency transformation is used to allow the parser to predict
    non-projective parses.

    The parser is trained using an imitation learning objective. The parser follows
    the actions predicted by the current weights, and at each state, determines
    which actions are compatible with the optimal parse that could be reached
    from the current state. The weights such that the scores assigned to the
    set of optimal actions is increased, while scores assigned to other
    actions are decreased. Note that more than one action may be optimal for
    a given state.

    model (Model): The model for the transition-based parser. The model needs
        to have a specific substructure of named components --- see the
        spacy.ml.tb_framework.TransitionModel for details.
    moves (List[str]): A list of transition names. Inferred from the data if not
        provided.
    update_with_oracle_cut_size (int):
        During training, cut long sequences into shorter segments by creating
        intermediate states based on the gold-standard history. The model is
        not very sensitive to this parameter, so you usually won't need to change
        it. 100 is a good default.
    learn_tokens (bool): Whether to learn to merge subtokens that are split
        relative to the gold standard. Experimental.
    min_action_freq (int): The minimum frequency of labelled actions to retain.
        Rarer labelled actions have their label backed-off to "dep". While this
        primarily affects the label accuracy, it can also affect the attachment
        structure, as the labels are used to represent the pseudo-projectivity
        transformation.
    """
    return DependencyParser(
        nlp.vocab,
        model,
        name,
        moves=moves,
        update_with_oracle_cut_size=update_with_oracle_cut_size,
        multitasks=[],
        learn_tokens=learn_tokens,
        min_action_freq=min_action_freq
    )


cdef class DependencyParser(Parser):
    """Pipeline component for dependency parsing.

    DOCS: https://nightly.spacy.io/api/dependencyparser
    """
    TransitionSystem = ArcEager

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
                label = move.split("-")[1]
                if "||" in label:
                    label = label.split("||")[1]
                labels.add(label)
        return tuple(sorted(labels))

    def score(self, examples, **kwargs):
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores, produced by Scorer.score_spans
            and Scorer.score_deps.

        DOCS: https://nightly.spacy.io/api/dependencyparser#score
        """
        validate_examples(examples, "DependencyParser.score")
        def dep_getter(token, attr):
            dep = getattr(token, attr)
            dep = token.vocab.strings.as_string(dep).lower()
            return dep
        results = {}
        results.update(Scorer.score_spans(examples, "sents", **kwargs))
        kwargs.setdefault("getter", dep_getter)
        kwargs.setdefault("ignore_labels", ("p", "punct"))
        results.update(Scorer.score_deps(examples, "dep", **kwargs))
        del results["sents_per_type"]
        return results
