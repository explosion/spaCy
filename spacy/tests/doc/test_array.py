import numpy
import pytest

from spacy.attrs import DEP, MORPH, ORTH, POS, SHAPE
from spacy.tokens import Doc


@pytest.mark.issue(2203)
def test_issue2203(en_vocab):
    """Test that lemmas are set correctly in doc.from_array."""
    words = ["I", "'ll", "survive"]
    tags = ["PRP", "MD", "VB"]
    lemmas = ["-PRON-", "will", "survive"]
    tag_ids = [en_vocab.strings.add(tag) for tag in tags]
    lemma_ids = [en_vocab.strings.add(lemma) for lemma in lemmas]
    doc = Doc(en_vocab, words=words)
    # Work around lemma corruption problem and set lemmas after tags
    doc.from_array("TAG", numpy.array(tag_ids, dtype="uint64"))
    doc.from_array("LEMMA", numpy.array(lemma_ids, dtype="uint64"))
    assert [t.tag_ for t in doc] == tags
    assert [t.lemma_ for t in doc] == lemmas
    # We need to serialize both tag and lemma, since this is what causes the bug
    doc_array = doc.to_array(["TAG", "LEMMA"])
    new_doc = Doc(doc.vocab, words=words).from_array(["TAG", "LEMMA"], doc_array)
    assert [t.tag_ for t in new_doc] == tags
    assert [t.lemma_ for t in new_doc] == lemmas


def test_doc_array_attr_of_token(en_vocab):
    doc = Doc(en_vocab, words=["An", "example", "sentence"])
    example = doc.vocab["example"]
    assert example.orth != example.shape
    feats_array = doc.to_array((ORTH, SHAPE))
    assert feats_array[0][0] != feats_array[0][1]
    assert feats_array[0][0] != feats_array[0][1]


def test_doc_stringy_array_attr_of_token(en_vocab):
    doc = Doc(en_vocab, words=["An", "example", "sentence"])
    example = doc.vocab["example"]
    assert example.orth != example.shape
    feats_array = doc.to_array((ORTH, SHAPE))
    feats_array_stringy = doc.to_array(("ORTH", "SHAPE"))
    assert feats_array_stringy[0][0] == feats_array[0][0]
    assert feats_array_stringy[0][1] == feats_array[0][1]


def test_doc_scalar_attr_of_token(en_vocab):
    doc = Doc(en_vocab, words=["An", "example", "sentence"])
    example = doc.vocab["example"]
    assert example.orth != example.shape
    feats_array = doc.to_array(ORTH)
    assert feats_array.shape == (3,)


def test_doc_array_tag(en_vocab):
    words = ["A", "nice", "sentence", "."]
    pos = ["DET", "ADJ", "NOUN", "PUNCT"]
    doc = Doc(en_vocab, words=words, pos=pos)
    assert doc[0].pos != doc[1].pos != doc[2].pos != doc[3].pos
    feats_array = doc.to_array((ORTH, POS))
    assert feats_array[0][1] == doc[0].pos
    assert feats_array[1][1] == doc[1].pos
    assert feats_array[2][1] == doc[2].pos
    assert feats_array[3][1] == doc[3].pos


def test_doc_array_morph(en_vocab):
    words = ["Eat", "blue", "ham"]
    morph = ["Feat=V", "Feat=J", "Feat=N"]
    doc = Doc(en_vocab, words=words, morphs=morph)
    assert morph[0] == str(doc[0].morph)
    assert morph[1] == str(doc[1].morph)
    assert morph[2] == str(doc[2].morph)

    feats_array = doc.to_array((ORTH, MORPH))
    assert feats_array[0][1] == doc[0].morph.key
    assert feats_array[1][1] == doc[1].morph.key
    assert feats_array[2][1] == doc[2].morph.key


def test_doc_array_dep(en_vocab):
    words = ["A", "nice", "sentence", "."]
    deps = ["det", "amod", "ROOT", "punct"]
    doc = Doc(en_vocab, words=words, deps=deps)
    feats_array = doc.to_array((ORTH, DEP))
    assert feats_array[0][1] == doc[0].dep
    assert feats_array[1][1] == doc[1].dep
    assert feats_array[2][1] == doc[2].dep
    assert feats_array[3][1] == doc[3].dep


@pytest.mark.parametrize("attrs", [["ORTH", "SHAPE"], "IS_ALPHA"])
def test_doc_array_to_from_string_attrs(en_vocab, attrs):
    """Test that both Doc.to_array and Doc.from_array accept string attrs,
    as well as single attrs and sequences of attrs.
    """
    words = ["An", "example", "sentence"]
    doc = Doc(en_vocab, words=words)
    Doc(en_vocab, words=words).from_array(attrs, doc.to_array(attrs))


def test_doc_array_idx(en_vocab):
    """Test that Doc.to_array can retrieve token start indices"""
    words = ["An", "example", "sentence"]
    offsets = Doc(en_vocab, words=words).to_array("IDX")
    assert offsets[0] == 0
    assert offsets[1] == 3
    assert offsets[2] == 11


def test_doc_from_array_heads_in_bounds(en_vocab):
    """Test that Doc.from_array doesn't set heads that are out of bounds."""
    words = ["This", "is", "a", "sentence", "."]
    doc = Doc(en_vocab, words=words)
    for token in doc:
        token.head = doc[0]

    # correct
    arr = doc.to_array(["HEAD"])
    doc_from_array = Doc(en_vocab, words=words)
    doc_from_array.from_array(["HEAD"], arr)

    # head before start
    arr = doc.to_array(["HEAD"])
    arr[0] = numpy.int32(-1).astype(numpy.uint64)
    doc_from_array = Doc(en_vocab, words=words)
    with pytest.raises(ValueError):
        doc_from_array.from_array(["HEAD"], arr)

    # head after end
    arr = doc.to_array(["HEAD"])
    arr[0] = numpy.int32(5).astype(numpy.uint64)
    doc_from_array = Doc(en_vocab, words=words)
    with pytest.raises(ValueError):
        doc_from_array.from_array(["HEAD"], arr)
