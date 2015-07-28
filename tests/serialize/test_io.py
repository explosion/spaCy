import pytest

from spacy.serialize.packer import Packer
from spacy.attrs import ORTH, SPACY
from spacy.tokens import Doc
import math


@pytest.mark.models
def test_read_write(EN):
    doc1 = EN(u'This is a simple test. With a couple of sentences.')
    doc2 = EN(u'This is another test document.')

    with open('/tmp/spacy_docs.bin', 'wb') as file_:
        file_.write(doc1.to_bytes())
        file_.write(doc2.to_bytes())

    with open('/tmp/spacy_docs.bin', 'rb') as file_:
        bytes1, bytes2 = Doc.read_bytes(file_)
        r1 = Doc(EN.vocab).from_bytes(bytes1)
        r2 = Doc(EN.vocab).from_bytes(bytes2)

    assert r1.string == doc1.string
    assert r2.string == doc2.string


@pytest.mark.models
def test_left_right(EN):
    orig = EN(u'This is a simple test. With a couple of sentences.')
    result = Doc(orig.vocab).from_bytes(orig.to_bytes())

    for word in result:
        assert word.head.i == orig[word.i].head.i
        if word.head is not word:
            assert word.i in [w.i for w in word.head.children]
        for child in word.lefts:
            assert child.head.i == word.i
        for child in word.rights:
            assert child.head.i == word.i

