# coding: utf-8
from __future__ import unicode_literals

from ...symbols import POS, VERB, VerbForm_inf
from ...vocab import Vocab
from ...lemmatizer import Lemmatizer
from ..util import get_doc

import pytest


def test_issue595():
    """Test lemmatization of base forms"""
    words = ["Do", "n't", "feed", "the", "dog"]
    tag_map = {'VB': {POS: VERB, 'morph': VerbForm_inf}}
    rules = {"verb": [["ed", "e"]]}

    lemmatizer = Lemmatizer({'verb': {}}, {'verb': {}}, rules)
    vocab = Vocab(lemmatizer=lemmatizer, tag_map=tag_map)
    doc = get_doc(vocab, words)

    doc[2].tag_ = 'VB'
    assert doc[2].text == 'feed'
    assert doc[2].lemma_ == 'feed'
