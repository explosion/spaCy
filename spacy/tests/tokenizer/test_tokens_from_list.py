from __future__ import unicode_literals
import pytest


def test1(en_tokenizer):
    words = ['JAPAN', 'GET', 'LUCKY']
    tokens = en_tokenizer.tokens_from_list(words)
    assert len(tokens) == 3
    assert tokens[0].orth_ == 'JAPAN'
