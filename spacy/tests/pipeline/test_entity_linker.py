import pytest

from spacy.kb import KnowledgeBase

from spacy import util, registry
from spacy.gold import Example
from spacy.lang.en import English
from spacy.tests.util import make_tempdir
from spacy.tokens import Span


@pytest.fixture
def nlp():
    return English()


def assert_almost_equal(a, b):
    delta = 0.0001
    assert a - delta <= b <= a + delta


def test_kb_valid_entities(nlp):
    """Test the valid construction of a KB with 3 entities and two aliases"""
    mykb = KnowledgeBase(entity_vector_length=3)
    mykb.initialize(nlp.vocab)

    # adding entities
    mykb.add_entity(entity="Q1", freq=19, entity_vector=[8, 4, 3])
    mykb.add_entity(entity="Q2", freq=5, entity_vector=[2, 1, 0])
    mykb.add_entity(entity="Q3", freq=25, entity_vector=[-1, -6, 5])

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
    mykb = KnowledgeBase(entity_vector_length=1)
    mykb.initialize(nlp.vocab)

    # adding entities
    mykb.add_entity(entity="Q1", freq=19, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=5, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=25, entity_vector=[3])

    # adding aliases - should fail because one of the given IDs is not valid
    with pytest.raises(ValueError):
        mykb.add_alias(
            alias="douglas", entities=["Q2", "Q342"], probabilities=[0.8, 0.2]
        )


def test_kb_invalid_probabilities(nlp):
    """Test the invalid construction of a KB with wrong prior probabilities"""
    mykb = KnowledgeBase(entity_vector_length=1)
    mykb.initialize(nlp.vocab)

    # adding entities
    mykb.add_entity(entity="Q1", freq=19, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=5, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=25, entity_vector=[3])

    # adding aliases - should fail because the sum of the probabilities exceeds 1
    with pytest.raises(ValueError):
        mykb.add_alias(alias="douglas", entities=["Q2", "Q3"], probabilities=[0.8, 0.4])


def test_kb_invalid_combination(nlp):
    """Test the invalid construction of a KB with non-matching entity and probability lists"""
    mykb = KnowledgeBase(entity_vector_length=1)
    mykb.initialize(nlp.vocab)

    # adding entities
    mykb.add_entity(entity="Q1", freq=19, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=5, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=25, entity_vector=[3])

    # adding aliases - should fail because the entities and probabilities vectors are not of equal length
    with pytest.raises(ValueError):
        mykb.add_alias(
            alias="douglas", entities=["Q2", "Q3"], probabilities=[0.3, 0.4, 0.1]
        )


def test_kb_invalid_entity_vector(nlp):
    """Test the invalid construction of a KB with non-matching entity vector lengths"""
    mykb = KnowledgeBase(entity_vector_length=3)
    mykb.initialize(nlp.vocab)

    # adding entities
    mykb.add_entity(entity="Q1", freq=19, entity_vector=[1, 2, 3])

    # this should fail because the kb's expected entity vector length is 3
    with pytest.raises(ValueError):
        mykb.add_entity(entity="Q2", freq=5, entity_vector=[2])


def test_kb_default(nlp):
    """Test that the default (empty) KB is loaded when not providing a config"""
    entity_linker = nlp.add_pipe("entity_linker", config={})
    assert len(entity_linker.kb) == 0
    assert entity_linker.kb.get_size_entities() == 0
    assert entity_linker.kb.get_size_aliases() == 0
    # default value from pipeline.entity_linker
    assert entity_linker.kb.entity_vector_length == 64


def test_kb_custom_length(nlp):
    """Test that the default (empty) KB can be configured with a custom entity length"""
    entity_linker = nlp.add_pipe(
        "entity_linker", config={"kb": {"entity_vector_length": 35}}
    )
    assert len(entity_linker.kb) == 0
    assert entity_linker.kb.get_size_entities() == 0
    assert entity_linker.kb.get_size_aliases() == 0
    assert entity_linker.kb.entity_vector_length == 35


def test_kb_undefined(nlp):
    """Test that the EL can't train without defining a KB"""
    entity_linker = nlp.add_pipe("entity_linker", config={})
    with pytest.raises(ValueError):
        entity_linker.begin_training(lambda: [])


def test_kb_empty(nlp):
    """Test that the EL can't train with an empty KB"""
    config = {"kb": {"@assets": "spacy.EmptyKB.v1", "entity_vector_length": 342}}
    entity_linker = nlp.add_pipe("entity_linker", config=config)
    assert len(entity_linker.kb) == 0
    with pytest.raises(ValueError):
        entity_linker.begin_training(lambda: [])


def test_candidate_generation(nlp):
    """Test correct candidate generation"""
    mykb = KnowledgeBase(entity_vector_length=1)
    mykb.initialize(nlp.vocab)

    # adding entities
    mykb.add_entity(entity="Q1", freq=27, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=12, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=5, entity_vector=[3])

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
    assert_almost_equal(mykb.get_candidates("adam")[0].entity_freq, 12)
    assert_almost_equal(mykb.get_candidates("adam")[0].prior_prob, 0.9)


def test_append_alias(nlp):
    """Test that we can append additional alias-entity pairs"""
    mykb = KnowledgeBase(entity_vector_length=1)
    mykb.initialize(nlp.vocab)

    # adding entities
    mykb.add_entity(entity="Q1", freq=27, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=12, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=5, entity_vector=[3])

    # adding aliases
    mykb.add_alias(alias="douglas", entities=["Q2", "Q3"], probabilities=[0.4, 0.1])
    mykb.add_alias(alias="adam", entities=["Q2"], probabilities=[0.9])

    # test the size of the relevant candidates
    assert len(mykb.get_candidates("douglas")) == 2

    # append an alias
    mykb.append_alias(alias="douglas", entity="Q1", prior_prob=0.2)

    # test the size of the relevant candidates has been incremented
    assert len(mykb.get_candidates("douglas")) == 3

    # append the same alias-entity pair again should not work (will throw a warning)
    with pytest.warns(UserWarning):
        mykb.append_alias(alias="douglas", entity="Q1", prior_prob=0.3)

    # test the size of the relevant candidates remained unchanged
    assert len(mykb.get_candidates("douglas")) == 3


def test_append_invalid_alias(nlp):
    """Test that append an alias will throw an error if prior probs are exceeding 1"""
    mykb = KnowledgeBase(entity_vector_length=1)
    mykb.initialize(nlp.vocab)

    # adding entities
    mykb.add_entity(entity="Q1", freq=27, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=12, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=5, entity_vector=[3])

    # adding aliases
    mykb.add_alias(alias="douglas", entities=["Q2", "Q3"], probabilities=[0.8, 0.1])
    mykb.add_alias(alias="adam", entities=["Q2"], probabilities=[0.9])

    # append an alias - should fail because the entities and probabilities vectors are not of equal length
    with pytest.raises(ValueError):
        mykb.append_alias(alias="douglas", entity="Q1", prior_prob=0.2)


def test_preserving_links_asdoc(nlp):
    """Test that Span.as_doc preserves the existing entity links"""

    @registry.assets.register("myLocationsKB.v1")
    def dummy_kb() -> KnowledgeBase:
        mykb = KnowledgeBase(entity_vector_length=1)
        mykb.initialize(nlp.vocab)
        # adding entities
        mykb.add_entity(entity="Q1", freq=19, entity_vector=[1])
        mykb.add_entity(entity="Q2", freq=8, entity_vector=[1])
        # adding aliases
        mykb.add_alias(alias="Boston", entities=["Q1"], probabilities=[0.7])
        mykb.add_alias(alias="Denver", entities=["Q2"], probabilities=[0.6])
        return mykb

    # set up pipeline with NER (Entity Ruler) and NEL (prior probability only, model not trained)
    nlp.add_pipe("sentencizer")
    patterns = [
        {"label": "GPE", "pattern": "Boston"},
        {"label": "GPE", "pattern": "Denver"},
    ]
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(patterns)
    el_config = {"kb": {"@assets": "myLocationsKB.v1"}, "incl_prior": False}
    el_pipe = nlp.add_pipe("entity_linker", config=el_config, last=True)
    el_pipe.begin_training(lambda: [])
    el_pipe.incl_context = False
    el_pipe.incl_prior = True

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


def test_preserving_links_ents(nlp):
    """Test that doc.ents preserves KB annotations"""
    text = "She lives in Boston. He lives in Denver."
    doc = nlp(text)
    assert len(list(doc.ents)) == 0

    boston_ent = Span(doc, 3, 4, label="LOC", kb_id="Q1")
    doc.ents = [boston_ent]
    assert len(list(doc.ents)) == 1
    assert list(doc.ents)[0].label_ == "LOC"
    assert list(doc.ents)[0].kb_id_ == "Q1"


def test_preserving_links_ents_2(nlp):
    """Test that doc.ents preserves KB annotations"""
    text = "She lives in Boston. He lives in Denver."
    doc = nlp(text)
    assert len(list(doc.ents)) == 0

    loc = doc.vocab.strings.add("LOC")
    q1 = doc.vocab.strings.add("Q1")

    doc.ents = [(loc, q1, 3, 4)]
    assert len(list(doc.ents)) == 1
    assert list(doc.ents)[0].label_ == "LOC"
    assert list(doc.ents)[0].kb_id_ == "Q1"


# fmt: off
TRAIN_DATA = [
    ("Russ Cochran captured his first major title with his son as caddie.",
        {"links": {(0, 12): {"Q7381115": 0.0, "Q2146908": 1.0}},
         "entities": [(0, 12, "PERSON")]}),
    ("Russ Cochran his reprints include EC Comics.",
        {"links": {(0, 12): {"Q7381115": 1.0, "Q2146908": 0.0}},
         "entities": [(0, 12, "PERSON")]}),
    ("Russ Cochran has been publishing comic art.",
        {"links": {(0, 12): {"Q7381115": 1.0, "Q2146908": 0.0}},
         "entities": [(0, 12, "PERSON")]}),
    ("Russ Cochran was a member of University of Kentucky's golf team.",
        {"links": {(0, 12): {"Q7381115": 0.0, "Q2146908": 1.0}},
         "entities": [(0, 12, "PERSON"), (43, 51, "LOC")]}),
]
GOLD_entities = ["Q2146908", "Q7381115", "Q7381115", "Q2146908"]
# fmt: on


def test_overfitting_IO():
    # Simple test to try and quickly overfit the NEL component - ensuring the ML models work correctly
    nlp = English()
    nlp.add_pipe("sentencizer")

    # Add a custom component to recognize "Russ Cochran" as an entity for the example training data
    patterns = [
        {"label": "PERSON", "pattern": [{"LOWER": "russ"}, {"LOWER": "cochran"}]}
    ]
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(patterns)

    # Convert the texts to docs to make sure we have doc.ents set for the training examples
    train_examples = []
    for text, annotation in TRAIN_DATA:
        doc = nlp(text)
        train_examples.append(Example.from_dict(doc, annotation))

    @registry.assets.register("myOverfittingKB.v1")
    def dummy_kb() -> KnowledgeBase:
        # create artificial KB - assign same prior weight to the two russ cochran's
        # Q2146908 (Russ Cochran): American golfer
        # Q7381115 (Russ Cochran): publisher
        mykb = KnowledgeBase(entity_vector_length=3)
        mykb.initialize(nlp.vocab)
        mykb.add_entity(entity="Q2146908", freq=12, entity_vector=[6, -4, 3])
        mykb.add_entity(entity="Q7381115", freq=12, entity_vector=[9, 1, -7])
        mykb.add_alias(
            alias="Russ Cochran",
            entities=["Q2146908", "Q7381115"],
            probabilities=[0.5, 0.5],
        )
        return mykb

    # Create the Entity Linker component and add it to the pipeline
    nlp.add_pipe(
        "entity_linker", config={"kb": {"@assets": "myOverfittingKB.v1"}}, last=True
    )

    # train the NEL pipe
    optimizer = nlp.begin_training()
    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["entity_linker"] < 0.001

    # test the trained model
    predictions = []
    for text, annotation in TRAIN_DATA:
        doc = nlp(text)
        for ent in doc.ents:
            predictions.append(ent.kb_id_)
    assert predictions == GOLD_entities

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        assert nlp2.pipe_names == nlp.pipe_names
        predictions = []
        for text, annotation in TRAIN_DATA:
            doc2 = nlp2(text)
            for ent in doc2.ents:
                predictions.append(ent.kb_id_)
        assert predictions == GOLD_entities
