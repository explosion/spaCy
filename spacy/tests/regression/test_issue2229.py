# coding: utf8
from __future__ import unicode_literals

from spacy.language import Language
from spacy.lang.en.examples import sentences


def test_concat_simple_docs(en_vocab):
    nlp = Language(vocab=en_vocab)
    doc1 = nlp(sentences[0])
    doc2 = nlp(sentences[1])

    doc3 = nlp(" ".join(sentences[0:2]))

    doc4 = nlp.concat(doc1, doc2)

    assert doc3.text == doc4.text


def test_concat_delimiter_test(en_vocab):
    nlp = Language(vocab=en_vocab)
    doc1 = nlp(sentences[0])
    doc2 = nlp(sentences[1])

    doc3 = nlp("! ".join(sentences[0:2]))

    doc4 = nlp.concat(doc1, doc2, join_delimiter="! ")

    assert doc3.text == doc4.text
