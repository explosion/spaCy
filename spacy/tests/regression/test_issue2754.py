# coding: utf8
from __future__ import unicode_literals


def test_issue2754(en_tokenizer):
    """Test that words like 'a' and 'a.m.' don't get exceptional norm values."""
    a = en_tokenizer("a")
    assert a[0].norm_ == "a"
    am = en_tokenizer("am")
    assert am[0].norm_ == "am"
