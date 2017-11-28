# coding: utf8
from __future__ import unicode_literals


def test_issue1612(en_tokenizer):
    doc = en_tokenizer('The black cat purrs.')
    span = doc[1: 3]
    assert span.orth_ == span.text
