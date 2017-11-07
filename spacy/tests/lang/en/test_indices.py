# coding: utf-8
"""Test that token.idx correctly computes index into the original string."""


from __future__ import unicode_literals

import pytest


def test_en_simple_punct(en_tokenizer):
    text = "to walk, do foo"
    tokens = en_tokenizer(text)
    assert tokens[0].idx == 0
    assert tokens[1].idx == 3
    assert tokens[2].idx == 7
    assert tokens[3].idx == 9
    assert tokens[4].idx == 12


def test_en_complex_punct(en_tokenizer):
    text = "Tom (D., Ill.)!"
    tokens = en_tokenizer(text)
    assert tokens[0].idx == 0
    assert len(tokens[0]) == 3
    assert tokens[1].idx == 4
    assert len(tokens[1]) == 1
    assert tokens[2].idx == 5
    assert len(tokens[2]) == 2
    assert tokens[3].idx == 7
    assert len(tokens[3]) == 1
    assert tokens[4].idx == 9
    assert len(tokens[4]) == 4
    assert tokens[5].idx == 13
    assert tokens[6].idx == 14
