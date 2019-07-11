# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Doc
from spacy.matcher import Matcher

@pytest.mark.xfail
def test_issue3541(en_vocab):
    doc = Doc(en_vocab, words=["terrific", "group", "of", "people"])
    # Works
    m1 = Matcher(doc.vocab)
    m1.add("PAT", None, [{'LOWER' : "terrific"}, {"OP": "?"}, {'LOWER' : "group"}])
    m2 = Matcher(doc.vocab)
    m2.add("PAT", None, [{'LOWER' : "terrific"}, {"OP": "?"}, {"OP": "?"}, {'LOWER' : "group"}])
    matches1 = m1(doc)
    assert matches1 == [(doc.vocab.strings["PAT"], 0, 2)]
    matches2 = m2(doc)
    assert matches2 == [(doc.vocab.strings["PAT"], 0, 2)]
