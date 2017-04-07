# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', ["want/need"])
def test_issue891(en_tokenizer, text):
    """Test that / infixes are split correctly."""
    tokens = en_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text == "/"
