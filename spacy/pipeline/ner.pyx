# cython: infer_types=True, profile=True, binding=True
from typing import Optional, Iterable
from thinc.api import Model, Config

from .transition_parser cimport Parser
from ._parser_internals.ner cimport BiluoPushDown

from ..language import Language
from ..scorer import get_ner_prf, PRFScore
from ..training import validate_examples


default_model_config = """
[model]
@architectures = "spacy.TransitionBasedParser.v1"
state_type = "ner"
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
DEFAULT_NER_MODEL = Config().from_str(default_model_config)["model"]


@Language.factory(
    "ner",
    assigns=["doc.ents", "token.ent_iob", "token.ent_type"],
    default_config={
        "moves": None,
        "update_with_oracle_cut_size": 100,
        "model": DEFAULT_NER_MODEL,
    },
    default_score_weights={"ents_f": 1.0, "ents_p": 0.0, "ents_r": 0.0, "ents_per_type": None},

)
def make_ner(
    nlp: Language,
    name: str,
    model: Model,
    moves: Optional[list],
    update_with_oracle_cut_size: int,
):
    """Create a transition-based EntityRecognizer component. The entity recognizer
    identifies non-overlapping labelled spans of tokens.

    The transition-based algorithm used encodes certain assumptions that are
    effective for "traditional" named entity recognition tasks, but may not be
    a good fit for every span identification problem. Specifically, the loss
    function optimizes for whole entity accuracy, so if your inter-annotator
    agreement on boundary tokens is low, the component will likely perform poorly
    on your problem. The transition-based algorithm also assumes that the most
    decisive information about your entities will be close to their initial tokens.
    If your entities are long and characterised by tokens in their middle, the
    component will likely do poorly on your task.

    model (Model): The model for the transition-based parser. The model needs
        to have a specific substructure of named components --- see the
        spacy.ml.tb_framework.TransitionModel for details.
    moves (list[str]): A list of transition names. Inferred from the data if not
        provided.
    update_with_oracle_cut_size (int):
        During training, cut long sequences into shorter segments by creating
        intermediate states based on the gold-standard history. The model is
        not very sensitive to this parameter, so you usually won't need to change
        it. 100 is a good default.
    """
    return EntityRecognizer(
        nlp.vocab,
        model,
        name,
        moves=moves,
        update_with_oracle_cut_size=update_with_oracle_cut_size,
        multitasks=[],
        min_action_freq=1,
        learn_tokens=False,
    )


cdef class EntityRecognizer(Parser):
    """Pipeline component for named entity recognition.

    DOCS: https://nightly.spacy.io/api/entityrecognizer
    """
    TransitionSystem = BiluoPushDown

    def add_multitask_objective(self, mt_component):
        """Register another component as a multi-task objective. Experimental."""
        self._multitasks.append(mt_component)

    def init_multitask_objectives(self, get_examples, nlp=None, **cfg):
        """Setup multi-task objective components. Experimental and internal."""
        # TODO: transfer self.model.get_ref("tok2vec") to the multitask's model ?
        for labeller in self._multitasks:
            labeller.model.set_dim("nO", len(self.labels))
            if labeller.model.has_ref("output_layer"):
                labeller.model.get_ref("output_layer").set_dim("nO", len(self.labels))
            labeller.initialize(get_examples, nlp=nlp)

    @property
    def labels(self):
        # Get the labels from the model by looking at the available moves, e.g.
        # B-PERSON, I-PERSON, L-PERSON, U-PERSON
        labels = set(move.split("-")[1] for move in self.move_names
                     if move[0] in ("B", "I", "L", "U"))
        return tuple(sorted(labels))

    def score(self, examples, **kwargs):
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The NER precision, recall and f-scores.

        DOCS: https://nightly.spacy.io/api/entityrecognizer#score
        """
        validate_examples(examples, "EntityRecognizer.score")
        score_per_type = get_ner_prf(examples)
        totals = PRFScore()
        for prf in score_per_type.values():
            totals += prf
        return {
            "ents_p": totals.precision,
            "ents_r": totals.recall,
            "ents_f": totals.fscore,
            "ents_per_type": {k: v.to_dict() for k, v in score_per_type.items()},
        }
