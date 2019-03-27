# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc


@pytest.mark.xfail
def test_issue3331(en_vocab):
    """Test that duplicate patterns for different rules result in multiple
    matches, one per rule.
    """
    matcher = PhraseMatcher(en_vocab)
    matcher.add("A", None, Doc(en_vocab, words=["Barack", "Obama"]))
    matcher.add("B", None, Doc(en_vocab, words=["Barack", "Obama"]))
    doc = Doc(en_vocab, words=["Barack", "Obama", "lifts", "America"])
    matches = matcher(doc)
    assert len(matches) == 2
    match_ids = [en_vocab.strings[matches[0][0]], en_vocab.strings[matches[1][0]]]
    assert sorted(match_ids) == ["A", "B"]
