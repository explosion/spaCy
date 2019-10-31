# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.gold import GoldParse


@pytest.mark.parametrize(
    "text,words", [("A'B C", ["A", "'", "B", "C"]), ("A-B", ["A-B"])]
)
def test_gold_misaligned(en_tokenizer, text, words):
    doc = en_tokenizer(text)
    GoldParse(doc, words=words)
