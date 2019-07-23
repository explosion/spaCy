# coding: utf-8
from __future__ import unicode_literals

import pytest

from spacy.kb import KnowledgeBase
from spacy.lang.en import English
from spacy.pipeline import EntityRuler


@pytest.fixture
def nlp():
    return English()


def assert_almost_equal(a, b):
    delta = 0.0001
    assert a - delta <= b <= a + delta


def test_kb_valid_entities(nlp):
    """Test the valid construction of a KB with 3 entities and two aliases"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=3)

    # adding entities
    mykb.add_entity(entity="Q1", freq=0.9, entity_vector=[8, 4, 3])
    mykb.add_entity(entity="Q2", freq=0.5, entity_vector=[2, 1, 0])
    mykb.add_entity(entity="Q3", freq=0.5, entity_vector=[-1, -6, 5])

    # adding aliases
    mykb.add_alias(alias="douglas", entities=["Q2", "Q3"], probabilities=[0.8, 0.2])
    mykb.add_alias(alias="adam", entities=["Q2"], probabilities=[0.9])

    # test the size of the corresponding KB
    assert mykb.get_size_entities() == 3
    assert mykb.get_size_aliases() == 2

    # test retrieval of the entity vectors
    assert mykb.get_vector("Q1") == [8, 4, 3]
    assert mykb.get_vector("Q2") == [2, 1, 0]
    assert mykb.get_vector("Q3") == [-1, -6, 5]

    # test retrieval of prior probabilities
    assert_almost_equal(mykb.get_prior_prob(entity="Q2", alias="douglas"), 0.8)
    assert_almost_equal(mykb.get_prior_prob(entity="Q3", alias="douglas"), 0.2)
    assert_almost_equal(mykb.get_prior_prob(entity="Q342", alias="douglas"), 0.0)
    assert_almost_equal(mykb.get_prior_prob(entity="Q3", alias="douglassssss"), 0.0)


def test_kb_invalid_entities(nlp):
    """Test the invalid construction of a KB with an alias linked to a non-existing entity"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)

    # adding entities
    mykb.add_entity(entity="Q1", freq=0.9, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=0.2, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=0.5, entity_vector=[3])

    # adding aliases - should fail because one of the given IDs is not valid
    with pytest.raises(ValueError):
        mykb.add_alias(
            alias="douglas", entities=["Q2", "Q342"], probabilities=[0.8, 0.2]
        )


def test_kb_invalid_probabilities(nlp):
    """Test the invalid construction of a KB with wrong prior probabilities"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)

    # adding entities
    mykb.add_entity(entity="Q1", freq=0.9, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=0.2, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=0.5, entity_vector=[3])

    # adding aliases - should fail because the sum of the probabilities exceeds 1
    with pytest.raises(ValueError):
        mykb.add_alias(alias="douglas", entities=["Q2", "Q3"], probabilities=[0.8, 0.4])


def test_kb_invalid_combination(nlp):
    """Test the invalid construction of a KB with non-matching entity and probability lists"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)

    # adding entities
    mykb.add_entity(entity="Q1", freq=0.9, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=0.2, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=0.5, entity_vector=[3])

    # adding aliases - should fail because the entities and probabilities vectors are not of equal length
    with pytest.raises(ValueError):
        mykb.add_alias(
            alias="douglas", entities=["Q2", "Q3"], probabilities=[0.3, 0.4, 0.1]
        )


def test_kb_invalid_entity_vector(nlp):
    """Test the invalid construction of a KB with non-matching entity vector lengths"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=3)

    # adding entities
    mykb.add_entity(entity="Q1", freq=0.9, entity_vector=[1, 2, 3])

    # this should fail because the kb's expected entity vector length is 3
    with pytest.raises(ValueError):
        mykb.add_entity(entity="Q2", freq=0.2, entity_vector=[2])


def test_candidate_generation(nlp):
    """Test correct candidate generation"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)

    # adding entities
    mykb.add_entity(entity="Q1", freq=0.7, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=0.2, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=0.5, entity_vector=[3])

    # adding aliases
    mykb.add_alias(alias="douglas", entities=["Q2", "Q3"], probabilities=[0.8, 0.1])
    mykb.add_alias(alias="adam", entities=["Q2"], probabilities=[0.9])

    # test the size of the relevant candidates
    assert len(mykb.get_candidates("douglas")) == 2
    assert len(mykb.get_candidates("adam")) == 1
    assert len(mykb.get_candidates("shrubbery")) == 0

    # test the content of the candidates
    assert mykb.get_candidates("adam")[0].entity_ == "Q2"
    assert mykb.get_candidates("adam")[0].alias_ == "adam"
    assert_almost_equal(mykb.get_candidates("adam")[0].entity_freq, 0.2)
    assert_almost_equal(mykb.get_candidates("adam")[0].prior_prob, 0.9)


def test_preserving_links_asdoc(nlp):
    """Test that Span.as_doc preserves the existing entity links"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)

    # adding entities
    mykb.add_entity(entity="Q1", freq=0.9, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=0.8, entity_vector=[1])

    # adding aliases
    mykb.add_alias(alias="Boston", entities=["Q1"], probabilities=[0.7])
    mykb.add_alias(alias="Denver", entities=["Q2"], probabilities=[0.6])

    # set up pipeline with NER (Entity Ruler) and NEL (prior probability only, model not trained)
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer)

    ruler = EntityRuler(nlp)
    patterns = [
        {"label": "GPE", "pattern": "Boston"},
        {"label": "GPE", "pattern": "Denver"},
    ]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)

    el_pipe = nlp.create_pipe(name="entity_linker", config={"context_width": 64})
    el_pipe.set_kb(mykb)
    el_pipe.begin_training()
    el_pipe.context_weight = 0
    el_pipe.prior_weight = 1
    nlp.add_pipe(el_pipe, last=True)

    # test whether the entity links are preserved by the `as_doc()` function
    text = "She lives in Boston. He lives in Denver."
    doc = nlp(text)
    for ent in doc.ents:
        orig_text = ent.text
        orig_kb_id = ent.kb_id_
        sent_doc = ent.sent.as_doc()
        for s_ent in sent_doc.ents:
            if s_ent.text == orig_text:
                assert s_ent.kb_id_ == orig_kb_id
