import pytest
from numpy.testing import assert_equal

from spacy import util
from spacy.attrs import SENT_START
from spacy.lang.en import English
from spacy.language import Language
from spacy.tests.util import make_tempdir
from spacy.training import Example


def test_label_types():
    nlp = Language()
    senter = nlp.add_pipe("senter")
    with pytest.raises(NotImplementedError):
        senter.add_label("A")


SENT_STARTS = [0] * 14
SENT_STARTS[0] = 1
SENT_STARTS[5] = 1
SENT_STARTS[9] = 1

TRAIN_DATA = [
    (
        "I like green eggs. Eat blue ham. I like purple eggs.",
        {"sent_starts": SENT_STARTS},
    ),
    (
        "She likes purple eggs. They hate ham. You like yellow eggs.",
        {"sent_starts": SENT_STARTS},
    ),
]


def test_initialize_examples():
    nlp = Language()
    nlp.add_pipe("senter")
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    # you shouldn't really call this more than once, but for testing it should be fine
    nlp.initialize()
    nlp.initialize(get_examples=lambda: train_examples)
    with pytest.raises(TypeError):
        nlp.initialize(get_examples=lambda: None)
    with pytest.raises(TypeError):
        nlp.initialize(get_examples=train_examples)


def test_overfitting_IO():
    # Simple test to try and quickly overfit the senter - ensuring the ML models work correctly
    nlp = English()
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    # add some cases where SENT_START == -1
    train_examples[0].reference[10].is_sent_start = False
    train_examples[1].reference[1].is_sent_start = False
    train_examples[1].reference[11].is_sent_start = False

    nlp.add_pipe("senter")
    optimizer = nlp.initialize()

    for i in range(200):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["senter"] < 0.001

    # test the trained model
    test_text = TRAIN_DATA[0][0]
    doc = nlp(test_text)
    gold_sent_starts = [0] * 14
    gold_sent_starts[0] = 1
    gold_sent_starts[5] = 1
    gold_sent_starts[9] = 1
    assert [int(t.is_sent_start) for t in doc] == gold_sent_starts

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        assert [int(t.is_sent_start) for t in doc2] == gold_sent_starts

    # Make sure that running pipe twice, or comparing to call, always amounts to the same predictions
    texts = [
        "Just a sentence.",
        "Then one more sentence about London.",
        "Here is another one.",
        "I like London.",
    ]
    batch_deps_1 = [doc.to_array([SENT_START]) for doc in nlp.pipe(texts)]
    batch_deps_2 = [doc.to_array([SENT_START]) for doc in nlp.pipe(texts)]
    no_batch_deps = [
        doc.to_array([SENT_START]) for doc in [nlp(text) for text in texts]
    ]
    assert_equal(batch_deps_1, batch_deps_2)
    assert_equal(batch_deps_1, no_batch_deps)

    # test internal pipe labels vs. Language.pipe_labels with hidden labels
    assert nlp.get_pipe("senter").labels == ("I", "S")
    assert "senter" not in nlp.pipe_labels
