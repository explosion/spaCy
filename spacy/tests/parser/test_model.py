import numpy
import pytest

from spacy.lang.en import English
from spacy.ml.tb_framework import TransitionModelInputs
from spacy.training import Example

TRAIN_DATA = [
    (
        "They trade mortgage-backed securities.",
        {
            "heads": [1, 1, 4, 4, 5, 1, 1],
            "deps": ["nsubj", "ROOT", "compound", "punct", "nmod", "dobj", "punct"],
        },
    ),
    (
        "I like London and Berlin.",
        {
            "heads": [1, 1, 1, 2, 2, 1],
            "deps": ["nsubj", "ROOT", "dobj", "cc", "conj", "punct"],
        },
    ),
]


@pytest.fixture
def nlp_parser():
    nlp = English()
    parser = nlp.add_pipe("parser")

    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for dep in annotations["deps"]:
            parser.add_label(dep)
    nlp.initialize()

    return nlp, parser


def test_incorrect_number_of_actions(nlp_parser):
    nlp, parser = nlp_parser
    doc = nlp.make_doc("test")

    # Too many actions for the number of docs
    with pytest.raises(AssertionError):
        parser.model.predict(
            TransitionModelInputs(
                docs=[doc], moves=parser.moves, actions=[numpy.array([0, 0], dtype="i")]
            )
        )

    # Too few actions for the number of docs
    with pytest.raises(AssertionError):
        parser.model.predict(
            TransitionModelInputs(
                docs=[doc, doc],
                moves=parser.moves,
                actions=[numpy.array([0], dtype="i")],
            )
        )
