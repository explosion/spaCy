# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc


def test_issue309(en_tokenizer):
    """Test Issue #309: SBD fails on empty string"""
    tokens = en_tokenizer(" ")
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=[0], deps=['ROOT'])
    doc.is_parsed = True
    assert len(doc) == 1
    sents = list(doc.sents)
    assert len(sents) == 1
