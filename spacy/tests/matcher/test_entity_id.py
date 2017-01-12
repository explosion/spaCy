# coding: utf-8
from __future__ import unicode_literals

from ...matcher import Matcher
from ...attrs import ORTH
from ..util import get_doc

import pytest


@pytest.mark.parametrize('words,entity', [
    (["Test", "Entity"], "TestEntity")])
def test_matcher_add_empty_entity(en_vocab, words, entity):
    matcher = Matcher(en_vocab)
    matcher.add_entity(entity)
    doc = get_doc(en_vocab, words)
    assert matcher.n_patterns == 0
    assert matcher(doc) == []


@pytest.mark.parametrize('entity1,entity2,attrs', [
    ("TestEntity", "TestEntity2", {"Hello": "World"})])
def test_matcher_get_entity_attrs(en_vocab, entity1, entity2, attrs):
    matcher = Matcher(en_vocab)
    matcher.add_entity(entity1)
    assert matcher.get_entity(entity1) == {}
    matcher.add_entity(entity2, attrs=attrs)
    assert matcher.get_entity(entity2) == attrs
    assert matcher.get_entity(entity1) == {}


@pytest.mark.parametrize('words,entity,attrs',
    [(["Test", "Entity"], "TestEntity", {"Hello": "World"})])
def test_matcher_get_entity_via_match(en_vocab, words, entity, attrs):
    matcher = Matcher(en_vocab)
    matcher.add_entity(entity, attrs=attrs)
    doc = get_doc(en_vocab, words)
    assert matcher.n_patterns == 0
    assert matcher(doc) == []

    matcher.add_pattern(entity, [{ORTH: words[0]}, {ORTH: words[1]}])
    assert matcher.n_patterns == 1

    matches = matcher(doc)
    assert len(matches) == 1
    assert len(matches[0]) == 4

    ent_id, label, start, end = matches[0]
    assert ent_id == matcher.vocab.strings[entity]
    assert label == 0
    assert start == 0
    assert end == 2
    assert matcher.get_entity(ent_id) == attrs
