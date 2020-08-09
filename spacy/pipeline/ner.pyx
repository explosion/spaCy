# cython: infer_types=True, profile=True, binding=True
from typing import Optional, Iterable
from thinc.api import Model, Config

from .transition_parser cimport Parser
from ._parser_internals.ner cimport BiluoPushDown

from ..language import Language
from ..scorer import Scorer


default_model_config = """
[model]
@architectures = "spacy.TransitionBasedParser.v1"
nr_feature_tokens = 6
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
    scores=["ents_p", "ents_r", "ents_f", "ents_per_type"],
    default_score_weights={"ents_f": 1.0, "ents_p": 0.0, "ents_r": 0.0},

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

    DOCS: https://spacy.io/api/entityrecognizer
    """
    TransitionSystem = BiluoPushDown

    def add_multitask_objective(self, mt_component):
        """Register another component as a multi-task objective. Experimental."""
        self._multitasks.append(mt_component)

    def init_multitask_objectives(self, get_examples, pipeline, sgd=None, **cfg):
        """Setup multi-task objective components. Experimental and internal."""
        # TODO: transfer self.model.get_ref("tok2vec") to the multitask's model ?
        for labeller in self._multitasks:
            labeller.model.set_dim("nO", len(self.labels))
            if labeller.model.has_ref("output_layer"):
                labeller.model.get_ref("output_layer").set_dim("nO", len(self.labels))
            labeller.begin_training(get_examples, pipeline=pipeline)

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
        RETURNS (Dict[str, Any]): The scores, produced by Scorer.score_spans.

        DOCS: https://spacy.io/api/entityrecognizer#score
        """
        return Scorer.score_spans(examples, "ents", **kwargs)
