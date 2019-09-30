# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.vocab import Vocab
from spacy.tokens import Doc
from spacy.lemmatizer import Lemmatizer


@pytest.fixture
def lemmatizer():
    return Lemmatizer(lookup={"dogs": "dog", "boxen": "box", "mice": "mouse"})


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
