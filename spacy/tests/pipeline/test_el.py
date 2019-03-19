# coding: utf-8
import pytest

from spacy.kb import KnowledgeBase


def test_kb_valid_entities():
    """Test the valid construction of a KB with 3 entities and one alias"""
    mykb = KnowledgeBase()

    # adding entities
    mykb.add_entity(entity_id="Q1", prob=0.9)
    mykb.add_entity(entity_id="Q2", prob=0.2)
    mykb.add_entity(entity_id="Q3", prob=0.5)

    # adding aliases
    mykb.add_alias(alias="douglas", entities=["Q2", "Q3"], probabilities=[0.8, 0.2])
    mykb.add_alias(alias="adam", entities=["Q2"], probabilities=[0.9])

    # test the size of the corresponding KB
    assert(mykb.get_size_entities() == 3)
    assert(mykb.get_size_aliases() == 2)


def test_kb_invalid_entities():
    """Test the invalid construction of a KB with an alias linked to a non-existing entity"""
    mykb = KnowledgeBase()

    # adding entities
    mykb.add_entity(entity_id="Q1", prob=0.9)
    mykb.add_entity(entity_id="Q2", prob=0.2)
    mykb.add_entity(entity_id="Q3", prob=0.5)

    # adding aliases - should fail because one of the given IDs is not valid
    with pytest.raises(ValueError):
        mykb.add_alias(alias="douglas", entities=["Q2", "Q342"], probabilities=[0.8, 0.2])


def test_kb_invalid_probabilities():
    """Test the invalid construction of a KB with wrong prior probabilities"""
    mykb = KnowledgeBase()

    # adding entities
    mykb.add_entity(entity_id="Q1", prob=0.9)
    mykb.add_entity(entity_id="Q2", prob=0.2)
    mykb.add_entity(entity_id="Q3", prob=0.5)

    # adding aliases - should fail because the sum of the probabilities exceeds 1
    with pytest.raises(ValueError):
        mykb.add_alias(alias="douglassss", entities=["Q2", "Q3"], probabilities=[0.8, 0.4])

