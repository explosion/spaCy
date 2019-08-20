# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.lang.en import English
from spacy.matcher import Matcher


@pytest.mark.xfail
def test_issue3879(en_vocab):
    nlp = English()
    text = "This is a test."
    doc = nlp(text)
    assert len(doc) == 5

    pattern = [{"ORTH": "This", "OP": "?"}, {"OP": "?"}, {"ORTH": "test"}]
    matcher = Matcher(nlp.vocab)
    matcher.add("rule", None, pattern)
    matches = matcher(doc)

    assert len(matches) == 2  # fails because of a FP match 'is a test'
