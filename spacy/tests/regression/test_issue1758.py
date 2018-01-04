# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', ["would've"])
def test_issue1758(en_tokenizer, text):
    """Test that "would've" is handled by the English tokenizer exceptions."""
    tokens = en_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[0].tag_ == "MD"
    assert tokens[1].lemma_ == "have"
