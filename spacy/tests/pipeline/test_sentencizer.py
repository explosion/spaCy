# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.pipeline import Sentencizer
from spacy.tokens import Doc


def test_sentencizer(en_vocab):
    doc = Doc(en_vocab, words=["Hello", "!", "This", "is", "a", "test", "."])
    sentencizer = Sentencizer()
    doc = sentencizer(doc)
    assert doc.is_sentenced
    sent_starts = [t.is_sent_start for t in doc]
    assert sent_starts == [True, False, True, False, False, False, False]
    assert len(list(doc.sents)) == 2


@pytest.mark.parametrize(
    "words,sent_starts,n_sents",
    [
        # The expected result here is that the duplicate punctuation gets merged
        # onto the same sentence and no one-token sentence is created for them.
        (
            ["Hello", "!", ".", "Test", ".", ".", "ok"],
            [True, False, False, True, False, False, True],
            3,
        ),
        # We also want to make sure ¡ and ¿ aren't treated as sentence end
        # markers, even though they're punctuation
        (
            ["¡", "Buen", "día", "!", "Hola", ",", "¿", "qué", "tal", "?"],
            [True, False, False, False, True, False, False, False, False, False],
            2,
        ),
        # The Token.is_punct check ensures that quotes are handled as well
        (
            ['"', "Nice", "!", '"', "I", "am", "happy", "."],
            [True, False, False, False, True, False, False, False],
            2,
        ),
    ],
)
def test_sentencizer_complex(en_vocab, words, sent_starts, n_sents):
    doc = Doc(en_vocab, words=words)
    sentencizer = Sentencizer()
    doc = sentencizer(doc)
    assert doc.is_sentenced
    assert [t.is_sent_start for t in doc] == sent_starts
    assert len(list(doc.sents)) == n_sents


@pytest.mark.parametrize(
    "punct_chars,words,sent_starts,n_sents",
    [
        (
            ["~", "?"],
            ["Hello", "world", "~", "A", ".", "B", "."],
            [True, False, False, True, False, False, False],
            2,
        ),
        # Even thought it's not common, the punct_chars should be able to
        # handle any tokens
        (
            [".", "ö"],
            ["Hello", ".", "Test", "ö", "Ok", "."],
            [True, False, True, False, True, False],
            3,
        ),
    ],
)
def test_sentencizer_custom_punct(en_vocab, punct_chars, words, sent_starts, n_sents):
    doc = Doc(en_vocab, words=words)
    sentencizer = Sentencizer(punct_chars=punct_chars)
    doc = sentencizer(doc)
    assert doc.is_sentenced
    assert [t.is_sent_start for t in doc] == sent_starts
    assert len(list(doc.sents)) == n_sents


def test_sentencizer_serialize_bytes(en_vocab):
    punct_chars = [".", "~", "+"]
    sentencizer = Sentencizer(punct_chars=punct_chars)
    assert sentencizer.punct_chars == punct_chars
    bytes_data = sentencizer.to_bytes()
    new_sentencizer = Sentencizer().from_bytes(bytes_data)
    assert new_sentencizer.punct_chars == punct_chars
