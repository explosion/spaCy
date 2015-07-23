import pytest

from spacy.serialize.packer import Packer
from spacy.attrs import ORTH, SPACY
from spacy.tokens import Doc
import math


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
