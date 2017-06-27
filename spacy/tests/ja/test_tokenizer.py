# coding: utf-8
from __future__ import unicode_literals

import pytest

def test_japanese_tokenizer(ja_tokenizer):
    tokens = ja_tokenizer("日本語だよ")
    assert len(tokens) == 3
