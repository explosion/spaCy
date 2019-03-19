import pytest

from spacy.kb import KnowledgeBase


def test_kb_valid_entities():
    mykb = KnowledgeBase()

    # adding entities
    mykb.add_entity(entity_id="Q1", prob=0.5)
    mykb.add_entity(entity_id="Q2", prob=0.5)
    mykb.add_entity(entity_id="Q3", prob=0.5)

    # adding aliases
    mykb.add_alias(alias="douglassss", entities=["Q2", "Q3"], probabilities=[0.8, 0.2])


def test_kb_invalid_entities():
    mykb = KnowledgeBase()

    # adding entities
    mykb.add_entity(entity_id="Q1", prob=0.5)
    mykb.add_entity(entity_id="Q2", prob=0.5)
    mykb.add_entity(entity_id="Q3", prob=0.5)

    # adding aliases - should fail because one of the given IDs is not valid
    with pytest.raises(ValueError):
        mykb.add_alias(alias="douglassss", entities=["Q2", "Q342"], probabilities=[0.8, 0.2])

