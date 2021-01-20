# coding: utf8
from __future__ import unicode_literals


def test_issue6755(en_tokenizer):
    doc = en_tokenizer("This is a magnificent sentence.")
    span = doc[:0]
    assert span.text_with_ws == ""
    assert span.text == ""
