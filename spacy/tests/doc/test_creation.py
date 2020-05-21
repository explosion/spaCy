# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.vocab import Vocab
from spacy.tokens import Doc
from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups
from spacy import util


@pytest.fixture
def lemmatizer():
    lookups = Lookups()
    lookups.add_table("lemma_lookup", {"dogs": "dog", "boxen": "box", "mice": "mouse"})
    return Lemmatizer(lookups)


@pytest.fixture
def vocab(lemmatizer):
    return Vocab(lemmatizer=lemmatizer)


def test_empty_doc(vocab):
    doc = Doc(vocab)
    assert len(doc) == 0


def test_single_word(vocab):
    doc = Doc(vocab, words=["a"])
    assert doc.text == "a "
    doc = Doc(vocab, words=["a"], spaces=[False])
    assert doc.text == "a"


def test_lookup_lemmatization(vocab):
    doc = Doc(vocab, words=["dogs", "dogses"])
    assert doc[0].text == "dogs"
    assert doc[0].lemma_ == "dog"
    assert doc[1].text == "dogses"
    assert doc[1].lemma_ == "dogses"


def test_create_from_words_and_text(vocab):
    # no whitespace in words
    words = ["'", "dogs", "'", "run"]
    text = "  'dogs'\n\nrun  "
    (words, spaces) = util.get_words_and_spaces(words, text)
    doc = Doc(vocab, words=words, spaces=spaces)
    assert [t.text for t in doc] == ["  ", "'", "dogs", "'", "\n\n", "run", " "]
    assert [t.whitespace_ for t in doc] == ["", "", "", "", "", " ", ""]
    assert doc.text == text
    assert [t.text for t in doc if not t.text.isspace()] == [
        word for word in words if not word.isspace()
    ]

    # partial whitespace in words
    words = ["  ", "'", "dogs", "'", "\n\n", "run", " "]
    text = "  'dogs'\n\nrun  "
    (words, spaces) = util.get_words_and_spaces(words, text)
    doc = Doc(vocab, words=words, spaces=spaces)
    assert [t.text for t in doc] == ["  ", "'", "dogs", "'", "\n\n", "run", " "]
    assert [t.whitespace_ for t in doc] == ["", "", "", "", "", " ", ""]
    assert doc.text == text
    assert [t.text for t in doc if not t.text.isspace()] == [
        word for word in words if not word.isspace()
    ]

    # non-standard whitespace tokens
    words = [" ", " ", "'", "dogs", "'", "\n\n", "run"]
    text = "  'dogs'\n\nrun  "
    (words, spaces) = util.get_words_and_spaces(words, text)
    doc = Doc(vocab, words=words, spaces=spaces)
    assert [t.text for t in doc] == ["  ", "'", "dogs", "'", "\n\n", "run", " "]
    assert [t.whitespace_ for t in doc] == ["", "", "", "", "", " ", ""]
    assert doc.text == text
    assert [t.text for t in doc if not t.text.isspace()] == [
        word for word in words if not word.isspace()
    ]

    # mismatch between words and text
    with pytest.raises(ValueError):
        words = [" ", " ", "'", "dogs", "'", "\n\n", "run"]
        text = "  'dogs'\n\nrun  "
        (words, spaces) = util.get_words_and_spaces(words + ["away"], text)
