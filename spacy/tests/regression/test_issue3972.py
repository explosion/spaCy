# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc


@pytest.mark.xfail
def test_issue3972(en_vocab):
    """Test that the PhraseMatcher returns duplicates for duplicate match IDs.
    """
    matcher = PhraseMatcher(en_vocab)
    matcher.add("A", None, Doc(en_vocab, words=["New", "York"]))
    matcher.add("B", None, Doc(en_vocab, words=["New", "York"]))
    doc = Doc(en_vocab, words=["I", "live", "in", "New", "York"])
    matches = matcher(doc)
    assert len(matches) == 2
