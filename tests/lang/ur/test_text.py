# coding: utf-8
from __future__ import unicode_literals

import pytest


def test_ur_tokenizer_handles_long_text(ur_tokenizer):
    text = """اصل میں، رسوا ہونے کی ہمیں کچھ عادت سی ہو گئی ہے۔"""
    tokens = ur_tokenizer(text)
    assert len(tokens) == 14


@pytest.mark.parametrize("text,length", [("تحریر باسط حبیب", 3), ("میرا پاکستان", 2)])
def test_ur_tokenizer_handles_cnts(ur_tokenizer, text, length):
    tokens = ur_tokenizer(text)
    assert len(tokens) == length
