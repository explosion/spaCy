# coding: utf-8
from __future__ import unicode_literals

from ...symbols import POS, VERB, VerbForm_part
from ...vocab import Vocab
from ...lemmatizer import Lemmatizer
from ..util import get_doc

import pytest


def test_issue1387():
    tag_map = {'VBG': {POS: VERB, VerbForm_part: True}}
    index = {"verb": ("cope","cop")}
    exc = {"verb": {"coping": ("cope",)}}
    rules = {"verb": [["ing", ""]]}
    lemmatizer = Lemmatizer(index, exc, rules)
    vocab = Vocab(lemmatizer=lemmatizer, tag_map=tag_map)
    doc = get_doc(vocab, ["coping"])
    doc[0].tag_ = 'VBG'
    assert doc[0].text == "coping"
    assert doc[0].lemma_ == "cope"
