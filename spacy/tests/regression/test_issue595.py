# coding: utf-8
from __future__ import unicode_literals

from ...symbols import POS, VERB, VerbForm_inf
from ...tokens import Doc
from ...vocab import Vocab
from ...lemmatizer import Lemmatizer

import pytest


@pytest.fixture
def index():
    return {'verb': {}}

@pytest.fixture
def exceptions():
    return {'verb': {}}

@pytest.fixture
def rules():
    return {"verb": [["ed", "e"]]}

@pytest.fixture
def lemmatizer(index, exceptions, rules):
    return Lemmatizer(index, exceptions, rules)


@pytest.fixture
def tag_map():
    return {'VB': {POS: VERB, 'morph': VerbForm_inf}}


@pytest.fixture
def vocab(lemmatizer, tag_map):
    return Vocab(lemmatizer=lemmatizer, tag_map=tag_map)


def test_not_lemmatize_base_forms(vocab):
    doc = Doc(vocab, words=["Do", "n't", "feed", "the", "dog"])
    feed = doc[2]
    feed.tag_ = 'VB'
    assert feed.text == 'feed'
    assert feed.lemma_ == 'feed'
