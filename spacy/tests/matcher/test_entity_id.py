from __future__ import unicode_literals
import spacy
from spacy.vocab import Vocab
from spacy.matcher import Matcher
from spacy.tokens.doc import Doc
from spacy.attrs import *

import pytest


@pytest.fixture
def en_vocab():
    return spacy.get_lang_class('en').Defaults.create_vocab()


def test_init_matcher(en_vocab):
    matcher = Matcher(en_vocab)
    assert matcher.n_patterns == 0
    assert matcher(Doc(en_vocab, words=[u'Some', u'words'])) == []


def test_add_empty_entity(en_vocab):
    matcher = Matcher(en_vocab)
    matcher.add_entity('TestEntity')
    assert matcher.n_patterns == 0
    assert matcher(Doc(en_vocab, words=[u'Test', u'Entity'])) == []


def test_get_entity_attrs(en_vocab):
    matcher = Matcher(en_vocab)
    matcher.add_entity('TestEntity')
    entity = matcher.get_entity('TestEntity')
    assert entity == {} 
    matcher.add_entity('TestEntity2', attrs={'Hello': 'World'})
    entity = matcher.get_entity('TestEntity2')
    assert entity == {'Hello': 'World'} 
    assert matcher.get_entity('TestEntity') == {}


def test_get_entity_via_match(en_vocab):
    matcher = Matcher(en_vocab)
    matcher.add_entity('TestEntity', attrs={u'Hello': u'World'})
    assert matcher.n_patterns == 0
    assert matcher(Doc(en_vocab, words=[u'Test', u'Entity'])) == []
    matcher.add_pattern(u'TestEntity', [{ORTH: u'Test'}, {ORTH: u'Entity'}])
    assert matcher.n_patterns == 1
    matches = matcher(Doc(en_vocab, words=[u'Test', u'Entity']))
    assert len(matches) == 1
    assert len(matches[0]) == 4
    ent_id, label, start, end = matches[0]
    assert ent_id == matcher.vocab.strings[u'TestEntity']
    assert label == 0
    assert start == 0
    assert end == 2
    attrs = matcher.get_entity(ent_id)
    assert attrs == {u'Hello': u'World'}



