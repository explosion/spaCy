import pytest

from spacy import util
from spacy.training import Example
from spacy.lang.en import English
from spacy.language import Language
from spacy.tests.util import make_tempdir
from spacy.morphology import Morphology


def test_label_types():
    nlp = Language()
    morphologizer = nlp.add_pipe("morphologizer")
    morphologizer.add_label("Feat=A")
    with pytest.raises(ValueError):
        morphologizer.add_label(9)


TRAIN_DATA = [
    (
        "I like green eggs",
        {
            "morphs": ["Feat=N", "Feat=V", "Feat=J", "Feat=N"],
            "pos": ["NOUN", "VERB", "ADJ", "NOUN"],
        },
    ),
    # test combinations of morph+POS
    ("Eat blue ham", {"morphs": ["Feat=V", "", ""], "pos": ["", "ADJ", ""]}),
]


def test_no_label():
    nlp = Language()
    nlp.add_pipe("morphologizer")
    with pytest.raises(ValueError):
        nlp.initialize()


def test_implicit_label():
    nlp = Language()
    nlp.add_pipe("morphologizer")
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    nlp.initialize(get_examples=lambda: train_examples)


def test_no_resize():
    nlp = Language()
    morphologizer = nlp.add_pipe("morphologizer")
    morphologizer.add_label("POS" + Morphology.FIELD_SEP + "NOUN")
    morphologizer.add_label("POS" + Morphology.FIELD_SEP + "VERB")
    nlp.initialize()
    # this throws an error because the morphologizer can't be resized after initialization
    with pytest.raises(ValueError):
        morphologizer.add_label("POS" + Morphology.FIELD_SEP + "ADJ")


def test_initialize_examples():
    nlp = Language()
    morphologizer = nlp.add_pipe("morphologizer")
    morphologizer.add_label("POS" + Morphology.FIELD_SEP + "NOUN")
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
    # Simple test to try and quickly overfit the morphologizer - ensuring the ML models work correctly
    nlp = English()
    nlp.add_pipe("morphologizer")
    train_examples = []
    for inst in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(inst[0]), inst[1]))
    optimizer = nlp.initialize(get_examples=lambda: train_examples)

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["morphologizer"] < 0.00001

    # test the trained model
    test_text = "I like blue ham"
    doc = nlp(test_text)
    gold_morphs = ["Feat=N", "Feat=V", "", ""]
    gold_pos_tags = ["NOUN", "VERB", "ADJ", ""]
    assert [str(t.morph) for t in doc] == gold_morphs
    assert [t.pos_ for t in doc] == gold_pos_tags

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        assert [str(t.morph) for t in doc2] == gold_morphs
        assert [t.pos_ for t in doc2] == gold_pos_tags
