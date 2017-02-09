# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text,tokens', [
    ('"deserve,"--and', ['"', "deserve", ',"--', "and"]),
    ("exception;--exclusive", ["exception", ";--", "exclusive"]),
    ("day.--Is", ["day", ".--", "Is"]),
    ("refinement:--just", ["refinement", ":--", "just"]),
    ("memories?--To", ["memories", "?--", "To"]),
    ("Useful.=--Therefore", ["Useful", ".=--", "Therefore"]),
    ("=Hope.=--Pandora", ["=", "Hope", ".=--", "Pandora"])])
def test_issue801(en_tokenizer, text, tokens):
    """Test that special characters + hyphens are split correctly."""
    doc = en_tokenizer(text)
    assert len(doc) == len(tokens)
    assert [t.text for t in doc] == tokens
