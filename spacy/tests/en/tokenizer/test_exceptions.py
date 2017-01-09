# coding: utf-8
"""Test that tokenizer exceptions are handled correctly."""


from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', ["e.g.", "p.m.", "Jan.", "Dec.", "Inc."])
def test_tokenizer_handles_abbr(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 1


def test_tokenizer_handles_exc_in_text(en_tokenizer):
    text = "It's mediocre i.e. bad."
    tokens = en_tokenizer(text)
    assert len(tokens) == 6
    assert tokens[3].text == "i.e."
