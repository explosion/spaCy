# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', ["Datum:2014-06-02\nDokument:76467"])
def test_issue886(en_tokenizer, text):
    """Test that token.idx matches the original text index for texts with newlines."""
    doc = en_tokenizer(text)
    for token in doc:
        assert len(token.text) == len(token.text_with_ws)
        assert text[token.idx] == token.text[0]
