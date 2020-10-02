import pytest
import numpy
from spacy.training import Example
from spacy.lang.en import English
from spacy.pipeline import AttributeRuler
from spacy import util, registry
from spacy.tokens import Doc

from ..util import make_tempdir


@pytest.fixture
def nlp():
    return English()


@pytest.fixture
def pattern_dicts():
    return [
        {
            "patterns": [[{"ORTH": "a"}], [{"ORTH": "irrelevant"}]],
            "attrs": {"LEMMA": "the", "MORPH": "Case=Nom|Number=Plur"},
        },
        # one pattern sets the lemma
        {"patterns": [[{"ORTH": "test"}]], "attrs": {"LEMMA": "cat"}},
        # another pattern sets the morphology
        {
            "patterns": [[{"ORTH": "test"}]],
            "attrs": {"MORPH": "Case=Nom|Number=Sing"},
            "index": 0,
        },
    ]


@registry.misc("attribute_ruler_patterns")
def attribute_ruler_patterns():
    return [
        {
            "patterns": [[{"ORTH": "a"}], [{"ORTH": "irrelevant"}]],
            "attrs": {"LEMMA": "the", "MORPH": "Case=Nom|Number=Plur"},
        },
        # one pattern sets the lemma
        {"patterns": [[{"ORTH": "test"}]], "attrs": {"LEMMA": "cat"}},
        # another pattern sets the morphology
        {
            "patterns": [[{"ORTH": "test"}]],
            "attrs": {"MORPH": "Case=Nom|Number=Sing"},
            "index": 0,
        },
    ]


@pytest.fixture
def tag_map():
    return {
        ".": {"POS": "PUNCT", "PunctType": "peri"},
        ",": {"POS": "PUNCT", "PunctType": "comm"},
    }


@pytest.fixture
def morph_rules():
    return {"DT": {"the": {"POS": "DET", "LEMMA": "a", "Case": "Nom"}}}


def test_attributeruler_init(nlp, pattern_dicts):
    a = nlp.add_pipe("attribute_ruler")
    for p in pattern_dicts:
        a.add(**p)
    doc = nlp("This is a test.")
    assert doc[2].lemma_ == "the"
    assert str(doc[2].morph) == "Case=Nom|Number=Plur"
    assert doc[3].lemma_ == "cat"
    assert str(doc[3].morph) == "Case=Nom|Number=Sing"
    assert doc.has_annotation("LEMMA")
    assert doc.has_annotation("MORPH")


def test_attributeruler_init_patterns(nlp, pattern_dicts):
    # initialize with patterns
    nlp.add_pipe("attribute_ruler", config={"pattern_dicts": pattern_dicts})
    doc = nlp("This is a test.")
    assert doc[2].lemma_ == "the"
    assert str(doc[2].morph) == "Case=Nom|Number=Plur"
    assert doc[3].lemma_ == "cat"
    assert str(doc[3].morph) == "Case=Nom|Number=Sing"
    assert doc.has_annotation("LEMMA")
    assert doc.has_annotation("MORPH")
    nlp.remove_pipe("attribute_ruler")
    # initialize with patterns from asset
    nlp.add_pipe(
        "attribute_ruler",
        config={"pattern_dicts": {"@misc": "attribute_ruler_patterns"}},
    )
    doc = nlp("This is a test.")
    assert doc[2].lemma_ == "the"
    assert str(doc[2].morph) == "Case=Nom|Number=Plur"
    assert doc[3].lemma_ == "cat"
    assert str(doc[3].morph) == "Case=Nom|Number=Sing"
    assert doc.has_annotation("LEMMA")
    assert doc.has_annotation("MORPH")


def test_attributeruler_score(nlp, pattern_dicts):
    # initialize with patterns
    nlp.add_pipe("attribute_ruler", config={"pattern_dicts": pattern_dicts})
    doc = nlp("This is a test.")
    assert doc[2].lemma_ == "the"
    assert str(doc[2].morph) == "Case=Nom|Number=Plur"
    assert doc[3].lemma_ == "cat"
    assert str(doc[3].morph) == "Case=Nom|Number=Sing"

    dev_examples = [
        Example.from_dict(
            nlp.make_doc("This is a test."), {"lemmas": ["this", "is", "a", "cat", "."]}
        )
    ]
    scores = nlp.evaluate(dev_examples)
    # "cat" is the only correct lemma
    assert scores["lemma_acc"] == pytest.approx(0.2)
    # the empty morphs are correct
    assert scores["morph_acc"] == pytest.approx(0.6)


def test_attributeruler_rule_order(nlp):
    a = AttributeRuler(nlp.vocab)
    patterns = [
        {"patterns": [[{"TAG": "VBZ"}]], "attrs": {"POS": "VERB"}},
        {"patterns": [[{"TAG": "VBZ"}]], "attrs": {"POS": "NOUN"}},
    ]
    a.add_patterns(patterns)
    doc = Doc(
        nlp.vocab,
        words=["This", "is", "a", "test", "."],
        tags=["DT", "VBZ", "DT", "NN", "."],
    )
    doc = a(doc)
    assert doc[1].pos_ == "NOUN"


def test_attributeruler_tag_map(nlp, tag_map):
    a = AttributeRuler(nlp.vocab)
    a.load_from_tag_map(tag_map)
    doc = Doc(
        nlp.vocab,
        words=["This", "is", "a", "test", "."],
        tags=["DT", "VBZ", "DT", "NN", "."],
    )
    doc = a(doc)
    for i in range(len(doc)):
        if i == 4:
            assert doc[i].pos_ == "PUNCT"
            assert str(doc[i].morph) == "PunctType=peri"
        else:
            assert doc[i].pos_ == ""
            assert str(doc[i].morph) == ""


def test_attributeruler_morph_rules(nlp, morph_rules):
    a = AttributeRuler(nlp.vocab)
    a.load_from_morph_rules(morph_rules)
    doc = Doc(
        nlp.vocab,
        words=["This", "is", "the", "test", "."],
        tags=["DT", "VBZ", "DT", "NN", "."],
    )
    doc = a(doc)
    for i in range(len(doc)):
        if i != 2:
            assert doc[i].pos_ == ""
            assert str(doc[i].morph) == ""
        else:
            assert doc[2].pos_ == "DET"
            assert doc[2].lemma_ == "a"
            assert str(doc[2].morph) == "Case=Nom"


def test_attributeruler_indices(nlp):
    a = nlp.add_pipe("attribute_ruler")
    a.add(
        [[{"ORTH": "a"}, {"ORTH": "test"}]],
        {"LEMMA": "the", "MORPH": "Case=Nom|Number=Plur"},
        index=0,
    )
    a.add(
        [[{"ORTH": "This"}, {"ORTH": "is"}]],
        {"LEMMA": "was", "MORPH": "Case=Nom|Number=Sing"},
        index=1,
    )
    a.add([[{"ORTH": "a"}, {"ORTH": "test"}]], {"LEMMA": "cat"}, index=-1)

    text = "This is a test."
    doc = nlp(text)
    for i in range(len(doc)):
        if i == 1:
            assert doc[i].lemma_ == "was"
            assert str(doc[i].morph) == "Case=Nom|Number=Sing"
        elif i == 2:
            assert doc[i].lemma_ == "the"
            assert str(doc[i].morph) == "Case=Nom|Number=Plur"
        elif i == 3:
            assert doc[i].lemma_ == "cat"
        else:
            assert str(doc[i].morph) == ""
    # raises an error when trying to modify a token outside of the match
    a.add([[{"ORTH": "a"}, {"ORTH": "test"}]], {"LEMMA": "cat"}, index=2)
    with pytest.raises(ValueError):
        doc = nlp(text)
    # raises an error when trying to modify a token outside of the match
    a.add([[{"ORTH": "a"}, {"ORTH": "test"}]], {"LEMMA": "cat"}, index=10)
    with pytest.raises(ValueError):
        doc = nlp(text)


def test_attributeruler_patterns_prop(nlp, pattern_dicts):
    a = nlp.add_pipe("attribute_ruler")
    a.add_patterns(pattern_dicts)
    for p1, p2 in zip(pattern_dicts, a.patterns):
        assert p1["patterns"] == p2["patterns"]
        assert p1["attrs"] == p2["attrs"]
        if p1.get("index"):
            assert p1["index"] == p2["index"]


def test_attributeruler_serialize(nlp, pattern_dicts):
    a = nlp.add_pipe("attribute_ruler")
    a.add_patterns(pattern_dicts)
    text = "This is a test."
    attrs = ["ORTH", "LEMMA", "MORPH"]
    doc = nlp(text)
    # bytes roundtrip
    a_reloaded = AttributeRuler(nlp.vocab).from_bytes(a.to_bytes())
    assert a.to_bytes() == a_reloaded.to_bytes()
    doc1 = a_reloaded(nlp.make_doc(text))
    numpy.array_equal(doc.to_array(attrs), doc1.to_array(attrs))
    assert a.patterns == a_reloaded.patterns
    # disk roundtrip
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(text)
        assert nlp2.get_pipe("attribute_ruler").to_bytes() == a.to_bytes()
        assert numpy.array_equal(doc.to_array(attrs), doc2.to_array(attrs))
        assert a.patterns == nlp2.get_pipe("attribute_ruler").patterns
