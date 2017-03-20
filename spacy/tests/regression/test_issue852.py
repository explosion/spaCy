# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', ["au-delàs", "pair-programmâmes",
                                  "terra-formées", "σ-compacts"])
def test_issue852(fr_tokenizer, text):
    """Test that French tokenizer exceptions are imported correctly."""
    tokens = fr_tokenizer(text)
    assert len(tokens) == 1
