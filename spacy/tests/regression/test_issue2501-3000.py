# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.lang.en import English
from spacy.lang.ja import Japanese
from spacy.lang.xx import MultiLanguage
from spacy.language import Language
from spacy.matcher import Matcher
from spacy.tokens import Span
from spacy.vocab import Vocab
from spacy._ml import link_vectors_to_models
import numpy

from ..util import get_doc


def test_issue2564():
    """Test the tagger sets is_tagged correctly when used via Language.pipe."""
    nlp = Language()
    tagger = nlp.create_pipe("tagger")
    tagger.begin_training()  # initialise weights
    nlp.add_pipe(tagger)
    doc = nlp("hello world")
    assert doc.is_tagged
    docs = nlp.pipe(["hello", "world"])
    piped_doc = next(docs)
    assert piped_doc.is_tagged


def test_issue2569(en_tokenizer):
    """Test that operator + is greedy."""
    doc = en_tokenizer("It is May 15, 1993.")
    doc.ents = [Span(doc, 2, 6, label=doc.vocab.strings["DATE"])]
    matcher = Matcher(doc.vocab)
    matcher.add("RULE", None, [{"ENT_TYPE": "DATE", "OP": "+"}])
    matched = [doc[start:end] for _, start, end in matcher(doc)]
    matched = sorted(matched, key=len, reverse=True)
    assert len(matched) == 10
    assert len(matched[0]) == 4
    assert matched[0].text == "May 15, 1993"


@pytest.mark.parametrize(
    "text",
    [
        "ABLEItemColumn IAcceptance Limits of ErrorIn-Service Limits of ErrorColumn IIColumn IIIColumn IVColumn VComputed VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeCubic FeetCubic FeetCubic FeetCubic FeetCubic Feet1Up to 10.0100.0050.0100.005220.0200.0100.0200.010350.0360.0180.0360.0184100.0500.0250.0500.0255Over 100.5% of computed volume0.25% of computed volume0.5% of computed volume0.25% of computed volume TABLE ItemColumn IAcceptance Limits of ErrorIn-Service Limits of ErrorColumn IIColumn IIIColumn IVColumn VComputed VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeCubic FeetCubic FeetCubic FeetCubic FeetCubic Feet1Up to 10.0100.0050.0100.005220.0200.0100.0200.010350.0360.0180.0360.0184100.0500.0250.0500.0255Over 100.5% of computed volume0.25% of computed volume0.5% of computed volume0.25% of computed volume ItemColumn IAcceptance Limits of ErrorIn-Service Limits of ErrorColumn IIColumn IIIColumn IVColumn VComputed VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeCubic FeetCubic FeetCubic FeetCubic FeetCubic Feet1Up to 10.0100.0050.0100.005220.0200.0100.0200.010350.0360.0180.0360.0184100.0500.0250.0500.0255Over 100.5% of computed volume0.25% of computed volume0.5% of computed volume0.25% of computed volume",
        "oow.jspsearch.eventoracleopenworldsearch.technologyoraclesolarissearch.technologystoragesearch.technologylinuxsearch.technologyserverssearch.technologyvirtualizationsearch.technologyengineeredsystemspcodewwmkmppscem:",
    ],
)
def test_issue2626_2835(en_tokenizer, text):
    """Check that sentence doesn't cause an infinite loop in the tokenizer."""
    doc = en_tokenizer(text)
    assert doc


def test_issue2671():
    """Ensure the correct entity ID is returned for matches with quantifiers.
    See also #2675
    """
    nlp = English()
    matcher = Matcher(nlp.vocab)
    pattern_id = "test_pattern"
    pattern = [
        {"LOWER": "high"},
        {"IS_PUNCT": True, "OP": "?"},
        {"LOWER": "adrenaline"},
    ]
    matcher.add(pattern_id, None, pattern)
    doc1 = nlp("This is a high-adrenaline situation.")
    doc2 = nlp("This is a high adrenaline situation.")
    matches1 = matcher(doc1)
    for match_id, start, end in matches1:
        assert nlp.vocab.strings[match_id] == pattern_id
    matches2 = matcher(doc2)
    for match_id, start, end in matches2:
        assert nlp.vocab.strings[match_id] == pattern_id


def test_issue2754(en_tokenizer):
    """Test that words like 'a' and 'a.m.' don't get exceptional norm values."""
    a = en_tokenizer("a")
    assert a[0].norm_ == "a"
    am = en_tokenizer("am")
    assert am[0].norm_ == "am"


def test_issue2772(en_vocab):
    """Test that deprojectivization doesn't mess up sentence boundaries."""
    words = "When we write or communicate virtually , we can hide our true feelings .".split()
    # A tree with a non-projective (i.e. crossing) arc
    # The arcs (0, 4) and (2, 9) cross.
    heads = [4, 1, 7, -1, -2, -1, 3, 2, 1, 0, -1, -2, -1]
    deps = ["dep"] * len(heads)
    doc = get_doc(en_vocab, words=words, heads=heads, deps=deps)
    assert doc[1].is_sent_start is None


@pytest.mark.parametrize("text", ["-0.23", "+123,456", "±1"])
@pytest.mark.parametrize("lang_cls", [English, MultiLanguage])
def test_issue2782(text, lang_cls):
    """Check that like_num handles + and - before number."""
    nlp = lang_cls()
    doc = nlp(text)
    assert len(doc) == 1
    assert doc[0].like_num


def test_issue2871():
    """Test that vectors recover the correct key for spaCy reserved words."""
    words = ["dog", "cat", "SUFFIX"]
    vocab = Vocab()
    vocab.vectors.resize(shape=(3, 10))
    vector_data = numpy.zeros((3, 10), dtype="f")
    for word in words:
        _ = vocab[word]  # noqa: F841
        vocab.set_vector(word, vector_data[0])
    vocab.vectors.name = "dummy_vectors"
    link_vectors_to_models(vocab)
    assert vocab["dog"].rank == 0
    assert vocab["cat"].rank == 1
    assert vocab["SUFFIX"].rank == 2
    assert vocab.vectors.find(key="dog") == 0
    assert vocab.vectors.find(key="cat") == 1
    assert vocab.vectors.find(key="SUFFIX") == 2


def test_issue2901():
    """Test that `nlp` doesn't fail."""
    try:
        nlp = Japanese()
    except ImportError:
        pytest.skip()

    doc = nlp("pythonが大好きです")
    assert doc
