import pytest
from numpy.testing import assert_almost_equal, assert_equal
from thinc.api import get_current_ops

from spacy import util
from spacy.attrs import MORPH
from spacy.lang.en import English
from spacy.language import Language
from spacy.morphology import Morphology
from spacy.tests.util import make_tempdir
from spacy.tokens import Doc
from spacy.training import Example


def test_label_types():
    nlp = Language()
    morphologizer = nlp.add_pipe("morphologizer")
    morphologizer.add_label("Feat=A")
    with pytest.raises(ValueError):
        morphologizer.add_label(9)


TAGS = ["Feat=N", "Feat=V", "Feat=J"]

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


def test_label_smoothing():
    nlp = Language()
    morph_no_ls = nlp.add_pipe("morphologizer", "no_label_smoothing")
    morph_ls = nlp.add_pipe(
        "morphologizer", "label_smoothing", config=dict(label_smoothing=0.05)
    )
    train_examples = []
    losses = {}
    for tag in TAGS:
        morph_no_ls.add_label(tag)
        morph_ls.add_label(tag)
    for t in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))

    nlp.initialize(get_examples=lambda: train_examples)
    tag_scores, bp_tag_scores = morph_ls.model.begin_update(
        [eg.predicted for eg in train_examples]
    )
    ops = get_current_ops()
    no_ls_grads = ops.to_numpy(morph_no_ls.get_loss(train_examples, tag_scores)[1][0])
    ls_grads = ops.to_numpy(morph_ls.get_loss(train_examples, tag_scores)[1][0])
    assert_almost_equal(ls_grads / no_ls_grads, 0.94285715)


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

    # Make sure that running pipe twice, or comparing to call, always amounts to the same predictions
    texts = [
        "Just a sentence.",
        "Then one more sentence about London.",
        "Here is another one.",
        "I like London.",
    ]
    batch_deps_1 = [doc.to_array([MORPH]) for doc in nlp.pipe(texts)]
    batch_deps_2 = [doc.to_array([MORPH]) for doc in nlp.pipe(texts)]
    no_batch_deps = [doc.to_array([MORPH]) for doc in [nlp(text) for text in texts]]
    assert_equal(batch_deps_1, batch_deps_2)
    assert_equal(batch_deps_1, no_batch_deps)

    # Test without POS
    nlp.remove_pipe("morphologizer")
    nlp.add_pipe("morphologizer")
    for example in train_examples:
        for token in example.reference:
            token.pos_ = ""
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["morphologizer"] < 0.00001

    # Test the trained model
    test_text = "I like blue ham"
    doc = nlp(test_text)
    gold_morphs = ["Feat=N", "Feat=V", "", ""]
    gold_pos_tags = ["", "", "", ""]
    assert [str(t.morph) for t in doc] == gold_morphs
    assert [t.pos_ for t in doc] == gold_pos_tags

    # Test overwrite+extend settings
    # (note that "" is unset, "_" is set and empty)
    morphs = ["Feat=V", "Feat=N", "_"]
    doc = Doc(nlp.vocab, words=["blue", "ham", "like"], morphs=morphs)
    orig_morphs = [str(t.morph) for t in doc]
    orig_pos_tags = [t.pos_ for t in doc]
    morphologizer = nlp.get_pipe("morphologizer")

    # don't overwrite or extend
    morphologizer.cfg["overwrite"] = False
    doc = morphologizer(doc)
    assert [str(t.morph) for t in doc] == orig_morphs
    assert [t.pos_ for t in doc] == orig_pos_tags

    # overwrite and extend
    morphologizer.cfg["overwrite"] = True
    morphologizer.cfg["extend"] = True
    doc = Doc(nlp.vocab, words=["I", "like"], morphs=["Feat=A|That=A|This=A", ""])
    doc = morphologizer(doc)
    assert [str(t.morph) for t in doc] == ["Feat=N|That=A|This=A", "Feat=V"]

    # extend without overwriting
    morphologizer.cfg["overwrite"] = False
    morphologizer.cfg["extend"] = True
    doc = Doc(nlp.vocab, words=["I", "like"], morphs=["Feat=A|That=A|This=A", "That=B"])
    doc = morphologizer(doc)
    assert [str(t.morph) for t in doc] == ["Feat=A|That=A|This=A", "Feat=V|That=B"]

    # overwrite without extending
    morphologizer.cfg["overwrite"] = True
    morphologizer.cfg["extend"] = False
    doc = Doc(nlp.vocab, words=["I", "like"], morphs=["Feat=A|That=A|This=A", ""])
    doc = morphologizer(doc)
    assert [str(t.morph) for t in doc] == ["Feat=N", "Feat=V"]

    # Test with unset morph and partial POS
    nlp.remove_pipe("morphologizer")
    nlp.add_pipe("morphologizer")
    for example in train_examples:
        for token in example.reference:
            if token.text == "ham":
                token.pos_ = "NOUN"
            else:
                token.pos_ = ""
            token.set_morph(None)
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    assert nlp.get_pipe("morphologizer").labels is not None
    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["morphologizer"] < 0.00001

    # Test the trained model
    test_text = "I like blue ham"
    doc = nlp(test_text)
    gold_morphs = ["", "", "", ""]
    gold_pos_tags = ["NOUN", "NOUN", "NOUN", "NOUN"]
    assert [str(t.morph) for t in doc] == gold_morphs
    assert [t.pos_ for t in doc] == gold_pos_tags
