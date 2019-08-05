# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc


def test_issue4002(en_vocab):
    """Test that the PhraseMatcher can match on overwritten NORM attributes.
    """
    matcher = PhraseMatcher(en_vocab, attr="NORM")
    pattern1 = Doc(en_vocab, words=["c", "d"])
    assert [t.norm_ for t in pattern1] == ["c", "d"]
    matcher.add("TEST", None, pattern1)
    doc = Doc(en_vocab, words=["a", "b", "c", "d"])
    assert [t.norm_ for t in doc] == ["a", "b", "c", "d"]
    matches = matcher(doc)
    assert len(matches) == 1
    matcher = PhraseMatcher(en_vocab, attr="NORM")
    pattern2 = Doc(en_vocab, words=["1", "2"])
    pattern2[0].norm_ = "c"
    pattern2[1].norm_ = "d"
    assert [t.norm_ for t in pattern2] == ["c", "d"]
    matcher.add("TEST", None, pattern2)
    matches = matcher(doc)
    assert len(matches) == 1
