# coding: utf-8
from __future__ import unicode_literals


def test_issue3277(es_tokenizer):
    """Test that hyphens are split correctly as prefixes."""
    doc = es_tokenizer("—Yo me llamo... –murmuró el niño– Emilio Sánchez Pérez.")
    assert len(doc) == 14
    assert doc[0].text == "\u2014"
    assert doc[5].text == "\u2013"
    assert doc[9].text == "\u2013"
