import pytest

from spacy import util
from spacy.lang.en import English
from spacy.language import Language
from spacy.tests.util import make_tempdir


def test_label_types():
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe("senter"))
    with pytest.raises(NotImplementedError):
        nlp.get_pipe("senter").add_label("A")

SENT_STARTS = [0] * 14
SENT_STARTS[0] = 1
SENT_STARTS[5] = 1
SENT_STARTS[9] = 1

TRAIN_DATA = [
    ("I like green eggs. Eat blue ham. I like purple eggs.", {"sent_starts": SENT_STARTS}),
    ("She likes purple eggs. They hate ham. You like yellow eggs.", {"sent_starts": SENT_STARTS}),
]


def test_overfitting_IO():
    # Simple test to try and quickly overfit the senter - ensuring the ML models work correctly
    nlp = English()
    senter = nlp.create_pipe("senter")
    nlp.add_pipe(senter)
    optimizer = nlp.begin_training()

    for i in range(200):
        losses = {}
        nlp.update(TRAIN_DATA, sgd=optimizer, losses=losses)
    assert losses["senter"] < 0.0001

    # test the trained model
    test_text = "I like eggs. There is ham. She likes ham."
    doc = nlp(test_text)
    gold_sent_starts = [0] * 12
    gold_sent_starts[0] = 1
    gold_sent_starts[4] = 1
    gold_sent_starts[8] = 1
    assert gold_sent_starts == [int(t.is_sent_start) for t in doc]

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        assert gold_sent_starts == [int(t.is_sent_start) for t in doc2]
