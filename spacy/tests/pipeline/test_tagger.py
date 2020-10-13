import pytest
from spacy import util
from spacy.training import Example
from spacy.lang.en import English
from spacy.language import Language

from ..util import make_tempdir


def test_label_types():
    nlp = Language()
    tagger = nlp.add_pipe("tagger")
    tagger.add_label("A")
    with pytest.raises(ValueError):
        tagger.add_label(9)


def test_tagger_initialize_tag_map():
    """Test that Tagger.initialize() without gold tuples does not clobber
    the tag map."""
    nlp = Language()
    tagger = nlp.add_pipe("tagger")
    orig_tag_count = len(tagger.labels)
    tagger.add_label("A")
    nlp.initialize()
    assert orig_tag_count + 1 == len(nlp.get_pipe("tagger").labels)


TAGS = ("N", "V", "J")

TRAIN_DATA = [
    ("I like green eggs", {"tags": ["N", "V", "J", "N"]}),
    ("Eat blue ham", {"tags": ["V", "J", "N"]}),
]


def test_no_label():
    nlp = Language()
    nlp.add_pipe("tagger")
    with pytest.raises(ValueError):
        nlp.initialize()


def test_no_resize():
    nlp = Language()
    tagger = nlp.add_pipe("tagger")
    tagger.add_label("N")
    tagger.add_label("V")
    assert tagger.labels == ("N", "V")
    nlp.initialize()
    assert tagger.model.get_dim("nO") == 2
    # this throws an error because the tagger can't be resized after initialization
    with pytest.raises(ValueError):
        tagger.add_label("J")


def test_implicit_label():
    nlp = Language()
    nlp.add_pipe("tagger")
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    nlp.initialize(get_examples=lambda: train_examples)


def test_initialize_examples():
    nlp = Language()
    tagger = nlp.add_pipe("tagger")
    train_examples = []
    for tag in TAGS:
        tagger.add_label(tag)
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    # you shouldn't really call this more than once, but for testing it should be fine
    nlp.initialize()
    nlp.initialize(get_examples=lambda: train_examples)
    with pytest.raises(TypeError):
        nlp.initialize(get_examples=lambda: None)
    with pytest.raises(TypeError):
        nlp.initialize(get_examples=lambda: train_examples[0])
    with pytest.raises(TypeError):
        nlp.initialize(get_examples=lambda: [])
    with pytest.raises(TypeError):
        nlp.initialize(get_examples=train_examples)


def test_overfitting_IO():
    # Simple test to try and quickly overfit the tagger - ensuring the ML models work correctly
    nlp = English()
    tagger = nlp.add_pipe("tagger")
    train_examples = []
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    assert tagger.model.get_dim("nO") == len(TAGS)

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["tagger"] < 0.00001

    # test the trained model
    test_text = "I like blue eggs"
    doc = nlp(test_text)
    assert doc[0].tag_ is "N"
    assert doc[1].tag_ is "V"
    assert doc[2].tag_ is "J"
    assert doc[3].tag_ is "N"

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        assert doc2[0].tag_ is "N"
        assert doc2[1].tag_ is "V"
        assert doc2[2].tag_ is "J"
        assert doc2[3].tag_ is "N"


def test_tagger_requires_labels():
    nlp = English()
    nlp.add_pipe("tagger")
    with pytest.raises(ValueError):
        nlp.initialize()
