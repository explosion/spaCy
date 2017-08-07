# coding: utf-8
from __future__ import unicode_literals

import pytest

def test_japanese_tagger(japanese):
    doc = japanese.make_doc("このファイルには小さなテストが入っているよ")
    # note these both have the same raw tag, '連体詞,*,*,*'
    assert doc[0].pos_ == "DET"
    assert doc[4].pos_ == "ADJ"
