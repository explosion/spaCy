# coding: utf-8
from __future__ import unicode_literals

import pytest

from spacy.kb import KnowledgeBase
from spacy.lang.en import English


@pytest.fixture
def nlp():
    return English()


def test_kb_valid_entities(nlp):
    """Test the valid construction of a KB with 3 entities and two aliases"""
    mykb = KnowledgeBase(nlp.vocab)

    # adding entities
    mykb.add_entity(entity=u'Q1', prob=0.9)
    mykb.add_entity(entity=u'Q2')
    mykb.add_entity(entity=u'Q3', prob=0.5)

    # adding aliases
    mykb.add_alias(alias=u'douglas', entities=[u'Q2', u'Q3'], probabilities=[0.8, 0.2])
    mykb.add_alias(alias=u'adam', entities=[u'Q2'], probabilities=[0.9])

    # test the size of the corresponding KB
    assert(mykb.get_size_entities() == 3)
    assert(mykb.get_size_aliases() == 2)


def test_kb_invalid_entities(nlp):
    """Test the invalid construction of a KB with an alias linked to a non-existing entity"""
    mykb = KnowledgeBase(nlp.vocab)

    # adding entities
    mykb.add_entity(entity=u'Q1', prob=0.9)
    mykb.add_entity(entity=u'Q2', prob=0.2)
    mykb.add_entity(entity=u'Q3', prob=0.5)

    # adding aliases - should fail because one of the given IDs is not valid
    with pytest.raises(ValueError):
        mykb.add_alias(alias=u'douglas', entities=[u'Q2', u'Q342'], probabilities=[0.8, 0.2])


def test_kb_invalid_probabilities(nlp):
    """Test the invalid construction of a KB with wrong prior probabilities"""
    mykb = KnowledgeBase(nlp.vocab)

    # adding entities
    mykb.add_entity(entity=u'Q1', prob=0.9)
    mykb.add_entity(entity=u'Q2', prob=0.2)
    mykb.add_entity(entity=u'Q3', prob=0.5)

    # adding aliases - should fail because the sum of the probabilities exceeds 1
    with pytest.raises(ValueError):
        mykb.add_alias(alias=u'douglas', entities=[u'Q2', u'Q3'], probabilities=[0.8, 0.4])


def test_kb_invalid_combination(nlp):
    """Test the invalid construction of a KB with non-matching entity and probability lists"""
    mykb = KnowledgeBase(nlp.vocab)

    # adding entities
    mykb.add_entity(entity=u'Q1', prob=0.9)
    mykb.add_entity(entity=u'Q2', prob=0.2)
    mykb.add_entity(entity=u'Q3', prob=0.5)

    # adding aliases - should fail because the entities and probabilities vectors are not of equal length
    with pytest.raises(ValueError):
        mykb.add_alias(alias=u'douglas', entities=[u'Q2', u'Q3'], probabilities=[0.3, 0.4, 0.1])


def test_candidate_generation(nlp):
    """Test correct candidate generation"""
    mykb = KnowledgeBase(nlp.vocab)

    # adding entities
    mykb.add_entity(entity=u'Q1', prob=0.9)
    mykb.add_entity(entity=u'Q2', prob=0.2)
    mykb.add_entity(entity=u'Q3', prob=0.5)

    # adding aliases
    mykb.add_alias(alias=u'douglas', entities=[u'Q2', u'Q3'], probabilities=[0.8, 0.2])
    mykb.add_alias(alias=u'adam', entities=[u'Q2'], probabilities=[0.9])

    # test the size of the relevant candidates
    assert(len(mykb.get_candidates(u'douglas')) == 2)
    assert(len(mykb.get_candidates(u'adam')) == 1)
    assert(len(mykb.get_candidates(u'shrubbery')) == 0)
