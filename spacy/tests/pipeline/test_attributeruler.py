import pytest
import numpy
from spacy.lang.en import English
from spacy.pipeline import AttributeRuler
from spacy import util, registry

from ..util import get_doc, make_tempdir


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


@registry.assets("attribute_ruler_patterns")
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
    assert doc[2].morph_ == "Case=Nom|Number=Plur"
    assert doc[3].lemma_ == "cat"
    assert doc[3].morph_ == "Case=Nom|Number=Sing"


def test_attributeruler_init_patterns(nlp, pattern_dicts):
    # initialize with patterns
    nlp.add_pipe("attribute_ruler", config={"pattern_dicts": pattern_dicts})
    doc = nlp("This is a test.")
    assert doc[2].lemma_ == "the"
    assert doc[2].morph_ == "Case=Nom|Number=Plur"
    assert doc[3].lemma_ == "cat"
    assert doc[3].morph_ == "Case=Nom|Number=Sing"
    nlp.remove_pipe("attribute_ruler")
    # initialize with patterns from asset
    nlp.add_pipe(
        "attribute_ruler",
        config={"pattern_dicts": {"@assets": "attribute_ruler_patterns"}},
    )
    doc = nlp("This is a test.")
    assert doc[2].lemma_ == "the"
    assert doc[2].morph_ == "Case=Nom|Number=Plur"
    assert doc[3].lemma_ == "cat"
    assert doc[3].morph_ == "Case=Nom|Number=Sing"


def test_attributeruler_tag_map(nlp, tag_map):
    a = AttributeRuler(nlp.vocab)
    a.load_from_tag_map(tag_map)
    doc = get_doc(
        nlp.vocab,
        words=["This", "is", "a", "test", "."],
        tags=["DT", "VBZ", "DT", "NN", "."],
    )
    doc = a(doc)

    for i in range(len(doc)):
        if i == 4:
            assert doc[i].pos_ == "PUNCT"
            assert doc[i].morph_ == "PunctType=peri"
        else:
            assert doc[i].pos_ == ""
            assert doc[i].morph_ == ""


def test_attributeruler_morph_rules(nlp, morph_rules):
    a = AttributeRuler(nlp.vocab)
    a.load_from_morph_rules(morph_rules)
    doc = get_doc(
        nlp.vocab,
        words=["This", "is", "the", "test", "."],
        tags=["DT", "VBZ", "DT", "NN", "."],
    )
    doc = a(doc)

    for i in range(len(doc)):
        if i != 2:
            assert doc[i].pos_ == ""
            assert doc[i].morph_ == ""
        else:
            assert doc[2].pos_ == "DET"
            assert doc[2].lemma_ == "a"
            assert doc[2].morph_ == "Case=Nom"


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
            assert doc[i].morph_ == "Case=Nom|Number=Sing"
        elif i == 2:
            assert doc[i].lemma_ == "the"
            assert doc[i].morph_ == "Case=Nom|Number=Plur"
        elif i == 3:
            assert doc[i].lemma_ == "cat"
        else:
            assert doc[i].morph_ == ""

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

    # disk roundtrip
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(text)
        assert nlp2.get_pipe("attribute_ruler").to_bytes() == a.to_bytes()
        assert numpy.array_equal(doc.to_array(attrs), doc2.to_array(attrs))
