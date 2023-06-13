import pytest
from numpy.testing import assert_almost_equal, assert_equal
from thinc.api import compounding, get_current_ops

from spacy import util
from spacy.attrs import TAG
from spacy.lang.en import English
from spacy.language import Language
from spacy.training import Example

from ..util import make_tempdir


@pytest.mark.issue(4348)
def test_issue4348():
    """Test that training the tagger with empty data, doesn't throw errors"""
    nlp = English()
    example = Example.from_dict(nlp.make_doc(""), {"tags": []})
    TRAIN_DATA = [example, example]
    tagger = nlp.add_pipe("tagger")
    tagger.add_label("A")
    optimizer = nlp.initialize()
    for i in range(5):
        losses = {}
        batches = util.minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            nlp.update(batch, sgd=optimizer, losses=losses)


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

PARTIAL_DATA = [
    # partial annotation
    ("I like green eggs", {"tags": ["", "V", "J", ""]}),
    # misaligned partial annotation
    (
        "He hates green eggs",
        {
            "words": ["He", "hate", "s", "green", "eggs"],
            "tags": ["", "V", "S", "J", ""],
        },
    ),
]


def test_label_smoothing():
    nlp = Language()
    tagger_no_ls = nlp.add_pipe("tagger", "no_label_smoothing")
    tagger_ls = nlp.add_pipe(
        "tagger", "label_smoothing", config=dict(label_smoothing=0.05)
    )
    train_examples = []
    losses = {}
    for tag in TAGS:
        tagger_no_ls.add_label(tag)
        tagger_ls.add_label(tag)
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))

    nlp.initialize(get_examples=lambda: train_examples)
    tag_scores, bp_tag_scores = tagger_ls.model.begin_update(
        [eg.predicted for eg in train_examples]
    )
    ops = get_current_ops()
    no_ls_grads = ops.to_numpy(tagger_no_ls.get_loss(train_examples, tag_scores)[1][0])
    ls_grads = ops.to_numpy(tagger_ls.get_loss(train_examples, tag_scores)[1][0])
    assert_almost_equal(ls_grads / no_ls_grads, 0.925)


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


def test_no_data():
    # Test that the tagger provides a nice error when there's no tagging data / labels
    TEXTCAT_DATA = [
        ("I'm so happy.", {"cats": {"POSITIVE": 1.0, "NEGATIVE": 0.0}}),
        ("I'm so angry", {"cats": {"POSITIVE": 0.0, "NEGATIVE": 1.0}}),
    ]
    nlp = English()
    nlp.add_pipe("tagger")
    nlp.add_pipe("textcat")
    train_examples = []
    for t in TEXTCAT_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    with pytest.raises(ValueError):
        nlp.initialize(get_examples=lambda: train_examples)


def test_incomplete_data():
    # Test that the tagger works with incomplete information
    nlp = English()
    nlp.add_pipe("tagger")
    train_examples = []
    for t in PARTIAL_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["tagger"] < 0.00001

    # test the trained model
    test_text = "I like blue eggs"
    doc = nlp(test_text)
    assert doc[1].tag_ == "V"
    assert doc[2].tag_ == "J"


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
    assert doc[0].tag_ == "N"
    assert doc[1].tag_ == "V"
    assert doc[2].tag_ == "J"
    assert doc[3].tag_ == "N"

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        assert doc2[0].tag_ == "N"
        assert doc2[1].tag_ == "V"
        assert doc2[2].tag_ == "J"
        assert doc2[3].tag_ == "N"

    # Make sure that running pipe twice, or comparing to call, always amounts to the same predictions
    texts = [
        "Just a sentence.",
        "I like green eggs.",
        "Here is another one.",
        "I eat ham.",
    ]
    batch_deps_1 = [doc.to_array([TAG]) for doc in nlp.pipe(texts)]
    batch_deps_2 = [doc.to_array([TAG]) for doc in nlp.pipe(texts)]
    no_batch_deps = [doc.to_array([TAG]) for doc in [nlp(text) for text in texts]]
    assert_equal(batch_deps_1, batch_deps_2)
    assert_equal(batch_deps_1, no_batch_deps)

    # Try to unlearn the first 'N' tag with negative annotation
    neg_ex = Example.from_dict(nlp.make_doc(test_text), {"tags": ["!N", "V", "J", "N"]})

    for i in range(20):
        losses = {}
        nlp.update([neg_ex], sgd=optimizer, losses=losses)

    # test the "untrained" tag
    doc3 = nlp(test_text)
    assert doc3[0].tag_ != "N"


def test_tagger_requires_labels():
    nlp = English()
    nlp.add_pipe("tagger")
    with pytest.raises(ValueError):
        nlp.initialize()
