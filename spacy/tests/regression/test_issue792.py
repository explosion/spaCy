# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.xfail
@pytest.mark.parametrize('text', ["This is a string ", "This is a string\u0020"])
def test_issue792(en_tokenizer, text):
    """Test for Issue #792: Trailing whitespace is removed after parsing."""
    doc = en_tokenizer(text)
    assert doc.text_with_ws == text
