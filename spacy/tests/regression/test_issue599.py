# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc


def test_issue599(en_vocab):
    doc = get_doc(en_vocab)
    doc.is_tagged = True
    doc.is_parsed = True
    doc2 = get_doc(doc.vocab)
    doc2.from_bytes(doc.to_bytes())
    assert doc2.is_parsed
