# cython: infer_types=True, profile=True, binding=True
from typing import Optional, Iterable

from thinc.api import CosineDistance, to_categorical, get_array_module, Model

from ..syntax.nn_parser cimport Parser
from ..syntax.ner cimport BiluoPushDown

from .defaults import default_ner_config
from ..language import Language


@Language.factory(
    "ner",
    assigns=["doc.ents", "token.ent_iob", "token.ent_type"],
    default_config={
        "moves": None,
        "update_with_oracle_cut_size": 100,
        "multitasks": [],
        "learn_tokens": False,
        "min_action_freq": 30,
        **default_ner_config()
    }
)
def make_ner(
    nlp: Language,
    name: str,
    model: Model,
    moves: Optional[list],
    update_with_oracle_cut_size: int,
    multitasks: Iterable,
    learn_tokens: bool,
    min_action_freq: int
):
    return EntityRecognizer(
        nlp.vocab,
        model,
        name,
        moves=moves,
        update_with_oracle_cut_size=update_with_oracle_cut_size,
        multitasks=multitasks,
        learn_tokens=learn_tokens,
        min_action_freq=min_action_freq
    )


cdef class EntityRecognizer(Parser):
    """Pipeline component for named entity recognition.

    DOCS: https://spacy.io/api/entityrecognizer
    """
    TransitionSystem = BiluoPushDown

    def add_multitask_objective(self, mt_component):
        self._multitasks.append(mt_component)

    def init_multitask_objectives(self, get_examples, pipeline, sgd=None, **cfg):
        # TODO: transfer self.model.get_ref("tok2vec") to the multitask's model ?
        for labeller in self._multitasks:
            labeller.model.set_dim("nO", len(self.labels))
            if labeller.model.has_ref("output_layer"):
                labeller.model.get_ref("output_layer").set_dim("nO", len(self.labels))
            labeller.begin_training(get_examples, pipeline=pipeline)

    def __reduce__(self):
        return (EntityRecognizer, (self.vocab, self.model), (self.moves, self.cfg))

    def __getstate__(self):
        return self.moves, self.cfg

    def __setstate__(self, state):
        moves, config = state
        self.moves = moves
        self.cfg = config

    @property
    def labels(self):
        # Get the labels from the model by looking at the available moves, e.g.
        # B-PERSON, I-PERSON, L-PERSON, U-PERSON
        labels = set(move.split("-")[1] for move in self.move_names
                     if move[0] in ("B", "I", "L", "U"))
        return tuple(sorted(labels))
