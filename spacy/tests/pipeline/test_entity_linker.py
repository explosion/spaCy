from typing import Callable, Iterable
import pytest
from numpy.testing import assert_equal
from spacy.attrs import ENT_KB_ID
from spacy.compat import pickle
from spacy.kb import KnowledgeBase, get_candidates, Candidate
from spacy.vocab import Vocab

from spacy import util, registry
from spacy.ml import load_kb
from spacy.scorer import Scorer
from spacy.training import Example
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
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=3)

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
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)

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
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)

    # adding entities
    mykb.add_entity(entity="Q1", freq=19, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=5, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=25, entity_vector=[3])

    # adding aliases - should fail because the sum of the probabilities exceeds 1
    with pytest.raises(ValueError):
        mykb.add_alias(alias="douglas", entities=["Q2", "Q3"], probabilities=[0.8, 0.4])


def test_kb_invalid_combination(nlp):
    """Test the invalid construction of a KB with non-matching entity and probability lists"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)

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
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=3)

    # adding entities
    mykb.add_entity(entity="Q1", freq=19, entity_vector=[1, 2, 3])

    # this should fail because the kb's expected entity vector length is 3
    with pytest.raises(ValueError):
        mykb.add_entity(entity="Q2", freq=5, entity_vector=[2])


def test_kb_default(nlp):
    """Test that the default (empty) KB is loaded upon construction"""
    entity_linker = nlp.add_pipe("entity_linker", config={})
    assert len(entity_linker.kb) == 0
    assert entity_linker.kb.get_size_entities() == 0
    assert entity_linker.kb.get_size_aliases() == 0
    # 64 is the default value from pipeline.entity_linker
    assert entity_linker.kb.entity_vector_length == 64


def test_kb_custom_length(nlp):
    """Test that the default (empty) KB can be configured with a custom entity length"""
    entity_linker = nlp.add_pipe("entity_linker", config={"entity_vector_length": 35})
    assert len(entity_linker.kb) == 0
    assert entity_linker.kb.get_size_entities() == 0
    assert entity_linker.kb.get_size_aliases() == 0
    assert entity_linker.kb.entity_vector_length == 35


def test_kb_initialize_empty(nlp):
    """Test that the EL can't initialize without examples"""
    entity_linker = nlp.add_pipe("entity_linker")
    with pytest.raises(TypeError):
        entity_linker.initialize(lambda: [])


def test_kb_serialize(nlp):
    """Test serialization of the KB"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)
    with make_tempdir() as d:
        # normal read-write behaviour
        mykb.to_disk(d / "kb")
        mykb.from_disk(d / "kb")
        mykb.to_disk(d / "new" / "kb")
        mykb.from_disk(d / "new" / "kb")
        # allow overwriting an existing file
        mykb.to_disk(d / "kb")
        with pytest.raises(ValueError):
            # can not read from an unknown file
            mykb.from_disk(d / "unknown" / "kb")


def test_kb_serialize_vocab(nlp):
    """Test serialization of the KB and custom strings"""
    entity = "MyFunnyID"
    assert entity not in nlp.vocab.strings
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)
    assert not mykb.contains_entity(entity)
    mykb.add_entity(entity, freq=342, entity_vector=[3])
    assert mykb.contains_entity(entity)
    assert entity in mykb.vocab.strings
    with make_tempdir() as d:
        # normal read-write behaviour
        mykb.to_disk(d / "kb")
        mykb_new = KnowledgeBase(Vocab(), entity_vector_length=1)
        mykb_new.from_disk(d / "kb")
        assert entity in mykb_new.vocab.strings


def test_candidate_generation(nlp):
    """Test correct candidate generation"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)
    doc = nlp("douglas adam Adam shrubbery")

    douglas_ent = doc[0:1]
    adam_ent = doc[1:2]
    Adam_ent = doc[2:3]
    shrubbery_ent = doc[3:4]

    # adding entities
    mykb.add_entity(entity="Q1", freq=27, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=12, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=5, entity_vector=[3])

    # adding aliases
    mykb.add_alias(alias="douglas", entities=["Q2", "Q3"], probabilities=[0.8, 0.1])
    mykb.add_alias(alias="adam", entities=["Q2"], probabilities=[0.9])

    # test the size of the relevant candidates
    assert len(get_candidates(mykb, douglas_ent)) == 2
    assert len(get_candidates(mykb, adam_ent)) == 1
    assert len(get_candidates(mykb, Adam_ent)) == 0  # default case sensitive
    assert len(get_candidates(mykb, shrubbery_ent)) == 0

    # test the content of the candidates
    assert get_candidates(mykb, adam_ent)[0].entity_ == "Q2"
    assert get_candidates(mykb, adam_ent)[0].alias_ == "adam"
    assert_almost_equal(get_candidates(mykb, adam_ent)[0].entity_freq, 12)
    assert_almost_equal(get_candidates(mykb, adam_ent)[0].prior_prob, 0.9)


def test_el_pipe_configuration(nlp):
    """Test correct candidate generation as part of the EL pipe"""
    nlp.add_pipe("sentencizer")
    pattern = {"label": "PERSON", "pattern": [{"LOWER": "douglas"}]}
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns([pattern])

    def create_kb(vocab):
        kb = KnowledgeBase(vocab, entity_vector_length=1)
        kb.add_entity(entity="Q2", freq=12, entity_vector=[2])
        kb.add_entity(entity="Q3", freq=5, entity_vector=[3])
        kb.add_alias(alias="douglas", entities=["Q2", "Q3"], probabilities=[0.8, 0.1])
        return kb

    # run an EL pipe without a trained context encoder, to check the candidate generation step only
    entity_linker = nlp.add_pipe("entity_linker", config={"incl_context": False})
    entity_linker.set_kb(create_kb)
    # With the default get_candidates function, matching is case-sensitive
    text = "Douglas and douglas are not the same."
    doc = nlp(text)
    assert doc[0].ent_kb_id_ == "NIL"
    assert doc[1].ent_kb_id_ == ""
    assert doc[2].ent_kb_id_ == "Q2"

    def get_lowercased_candidates(kb, span):
        return kb.get_alias_candidates(span.text.lower())

    @registry.misc("spacy.LowercaseCandidateGenerator.v1")
    def create_candidates() -> Callable[[KnowledgeBase, "Span"], Iterable[Candidate]]:
        return get_lowercased_candidates

    # replace the pipe with a new one with with a different candidate generator
    entity_linker = nlp.replace_pipe(
        "entity_linker",
        "entity_linker",
        config={
            "incl_context": False,
            "get_candidates": {"@misc": "spacy.LowercaseCandidateGenerator.v1"},
        },
    )
    entity_linker.set_kb(create_kb)
    doc = nlp(text)
    assert doc[0].ent_kb_id_ == "Q2"
    assert doc[1].ent_kb_id_ == ""
    assert doc[2].ent_kb_id_ == "Q2"


def test_nel_nsents(nlp):
    """Test that n_sents can be set through the configuration"""
    entity_linker = nlp.add_pipe("entity_linker", config={})
    assert entity_linker.n_sents == 0
    entity_linker = nlp.replace_pipe(
        "entity_linker", "entity_linker", config={"n_sents": 2}
    )
    assert entity_linker.n_sents == 2


def test_vocab_serialization(nlp):
    """Test that string information is retained across storage"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)

    # adding entities
    mykb.add_entity(entity="Q1", freq=27, entity_vector=[1])
    q2_hash = mykb.add_entity(entity="Q2", freq=12, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=5, entity_vector=[3])

    # adding aliases
    mykb.add_alias(alias="douglas", entities=["Q2", "Q3"], probabilities=[0.4, 0.1])
    adam_hash = mykb.add_alias(alias="adam", entities=["Q2"], probabilities=[0.9])

    candidates = mykb.get_alias_candidates("adam")
    assert len(candidates) == 1
    assert candidates[0].entity == q2_hash
    assert candidates[0].entity_ == "Q2"
    assert candidates[0].alias == adam_hash
    assert candidates[0].alias_ == "adam"

    with make_tempdir() as d:
        mykb.to_disk(d / "kb")
        kb_new_vocab = KnowledgeBase(Vocab(), entity_vector_length=1)
        kb_new_vocab.from_disk(d / "kb")

        candidates = kb_new_vocab.get_alias_candidates("adam")
        assert len(candidates) == 1
        assert candidates[0].entity == q2_hash
        assert candidates[0].entity_ == "Q2"
        assert candidates[0].alias == adam_hash
        assert candidates[0].alias_ == "adam"

        assert kb_new_vocab.get_vector("Q2") == [2]
        assert_almost_equal(kb_new_vocab.get_prior_prob("Q2", "douglas"), 0.4)


def test_append_alias(nlp):
    """Test that we can append additional alias-entity pairs"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)

    # adding entities
    mykb.add_entity(entity="Q1", freq=27, entity_vector=[1])
    mykb.add_entity(entity="Q2", freq=12, entity_vector=[2])
    mykb.add_entity(entity="Q3", freq=5, entity_vector=[3])

    # adding aliases
    mykb.add_alias(alias="douglas", entities=["Q2", "Q3"], probabilities=[0.4, 0.1])
    mykb.add_alias(alias="adam", entities=["Q2"], probabilities=[0.9])

    # test the size of the relevant candidates
    assert len(mykb.get_alias_candidates("douglas")) == 2

    # append an alias
    mykb.append_alias(alias="douglas", entity="Q1", prior_prob=0.2)

    # test the size of the relevant candidates has been incremented
    assert len(mykb.get_alias_candidates("douglas")) == 3

    # append the same alias-entity pair again should not work (will throw a warning)
    with pytest.warns(UserWarning):
        mykb.append_alias(alias="douglas", entity="Q1", prior_prob=0.3)

    # test the size of the relevant candidates remained unchanged
    assert len(mykb.get_alias_candidates("douglas")) == 3


@pytest.mark.filterwarnings("ignore:\\[W036")
def test_append_invalid_alias(nlp):
    """Test that append an alias will throw an error if prior probs are exceeding 1"""
    mykb = KnowledgeBase(nlp.vocab, entity_vector_length=1)

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


@pytest.mark.filterwarnings("ignore:\\[W036")
def test_preserving_links_asdoc(nlp):
    """Test that Span.as_doc preserves the existing entity links"""
    vector_length = 1

    def create_kb(vocab):
        mykb = KnowledgeBase(vocab, entity_vector_length=vector_length)
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
    config = {"incl_prior": False}
    entity_linker = nlp.add_pipe("entity_linker", config=config, last=True)
    entity_linker.set_kb(create_kb)
    nlp.initialize()
    assert entity_linker.model.get_dim("nO") == vector_length

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
         "entities": [(0, 12, "PERSON")],
         "sent_starts": [1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}),
    ("Russ Cochran his reprints include EC Comics.",
        {"links": {(0, 12): {"Q7381115": 1.0, "Q2146908": 0.0}},
         "entities": [(0, 12, "PERSON")],
         "sent_starts": [1, -1, 0, 0, 0, 0, 0, 0]}),
    ("Russ Cochran has been publishing comic art.",
        {"links": {(0, 12): {"Q7381115": 1.0, "Q2146908": 0.0}},
         "entities": [(0, 12, "PERSON")],
         "sent_starts": [1, -1, 0, 0, 0, 0, 0, 0]}),
    ("Russ Cochran was a member of University of Kentucky's golf team.",
        {"links": {(0, 12): {"Q7381115": 0.0, "Q2146908": 1.0}},
         "entities": [(0, 12, "PERSON"), (43, 51, "LOC")],
         "sent_starts": [1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]})
]
GOLD_entities = ["Q2146908", "Q7381115", "Q7381115", "Q2146908"]
# fmt: on


def test_overfitting_IO():
    # Simple test to try and quickly overfit the NEL component - ensuring the ML models work correctly
    nlp = English()
    vector_length = 3
    assert "Q2146908" not in nlp.vocab.strings

    # Convert the texts to docs to make sure we have doc.ents set for the training examples
    train_examples = []
    for text, annotation in TRAIN_DATA:
        doc = nlp(text)
        train_examples.append(Example.from_dict(doc, annotation))

    def create_kb(vocab):
        # create artificial KB - assign same prior weight to the two russ cochran's
        # Q2146908 (Russ Cochran): American golfer
        # Q7381115 (Russ Cochran): publisher
        mykb = KnowledgeBase(vocab, entity_vector_length=vector_length)
        mykb.add_entity(entity="Q2146908", freq=12, entity_vector=[6, -4, 3])
        mykb.add_entity(entity="Q7381115", freq=12, entity_vector=[9, 1, -7])
        mykb.add_alias(
            alias="Russ Cochran",
            entities=["Q2146908", "Q7381115"],
            probabilities=[0.5, 0.5],
        )
        return mykb

    # Create the Entity Linker component and add it to the pipeline
    entity_linker = nlp.add_pipe("entity_linker", last=True)
    entity_linker.set_kb(create_kb)
    assert "Q2146908" in entity_linker.vocab.strings
    assert "Q2146908" in entity_linker.kb.vocab.strings

    # train the NEL pipe
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    assert entity_linker.model.get_dim("nO") == vector_length
    assert entity_linker.model.get_dim("nO") == entity_linker.kb.entity_vector_length

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["entity_linker"] < 0.001

    # adding additional components that are required for the entity_linker
    nlp.add_pipe("sentencizer", first=True)

    # Add a custom component to recognize "Russ Cochran" as an entity for the example training data
    patterns = [
        {"label": "PERSON", "pattern": [{"LOWER": "russ"}, {"LOWER": "cochran"}]}
    ]
    ruler = nlp.add_pipe("entity_ruler", before="entity_linker")
    ruler.add_patterns(patterns)

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
        assert "Q2146908" in nlp2.vocab.strings
        entity_linker2 = nlp2.get_pipe("entity_linker")
        assert "Q2146908" in entity_linker2.vocab.strings
        assert "Q2146908" in entity_linker2.kb.vocab.strings
        predictions = []
        for text, annotation in TRAIN_DATA:
            doc2 = nlp2(text)
            for ent in doc2.ents:
                predictions.append(ent.kb_id_)
        assert predictions == GOLD_entities

    # Make sure that running pipe twice, or comparing to call, always amounts to the same predictions
    texts = [
        "Russ Cochran captured his first major title with his son as caddie.",
        "Russ Cochran his reprints include EC Comics.",
        "Russ Cochran has been publishing comic art.",
        "Russ Cochran was a member of University of Kentucky's golf team.",
    ]
    batch_deps_1 = [doc.to_array([ENT_KB_ID]) for doc in nlp.pipe(texts)]
    batch_deps_2 = [doc.to_array([ENT_KB_ID]) for doc in nlp.pipe(texts)]
    no_batch_deps = [doc.to_array([ENT_KB_ID]) for doc in [nlp(text) for text in texts]]
    assert_equal(batch_deps_1, batch_deps_2)
    assert_equal(batch_deps_1, no_batch_deps)


def test_kb_serialization():
    # Test that the KB can be used in a pipeline with a different vocab
    vector_length = 3
    with make_tempdir() as tmp_dir:
        kb_dir = tmp_dir / "kb"
        nlp1 = English()
        assert "Q2146908" not in nlp1.vocab.strings
        mykb = KnowledgeBase(nlp1.vocab, entity_vector_length=vector_length)
        mykb.add_entity(entity="Q2146908", freq=12, entity_vector=[6, -4, 3])
        mykb.add_alias(alias="Russ Cochran", entities=["Q2146908"], probabilities=[0.8])
        assert "Q2146908" in nlp1.vocab.strings
        mykb.to_disk(kb_dir)

        nlp2 = English()
        assert "RandomWord" not in nlp2.vocab.strings
        nlp2.vocab.strings.add("RandomWord")
        assert "RandomWord" in nlp2.vocab.strings
        assert "Q2146908" not in nlp2.vocab.strings

        # Create the Entity Linker component with the KB from file, and check the final vocab
        entity_linker = nlp2.add_pipe("entity_linker", last=True)
        entity_linker.set_kb(load_kb(kb_dir))
        assert "Q2146908" in nlp2.vocab.strings
        assert "RandomWord" in nlp2.vocab.strings


@pytest.mark.xfail(reason="Needs fixing")
def test_kb_pickle():
    # Test that the KB can be pickled
    nlp = English()
    kb_1 = KnowledgeBase(nlp.vocab, entity_vector_length=3)
    kb_1.add_entity(entity="Q2146908", freq=12, entity_vector=[6, -4, 3])
    assert not kb_1.contains_alias("Russ Cochran")
    kb_1.add_alias(alias="Russ Cochran", entities=["Q2146908"], probabilities=[0.8])
    assert kb_1.contains_alias("Russ Cochran")
    data = pickle.dumps(kb_1)
    kb_2 = pickle.loads(data)
    assert kb_2.contains_alias("Russ Cochran")


@pytest.mark.xfail(reason="Needs fixing")
def test_nel_pickle():
    # Test that a pipeline with an EL component can be pickled
    def create_kb(vocab):
        kb = KnowledgeBase(vocab, entity_vector_length=3)
        kb.add_entity(entity="Q2146908", freq=12, entity_vector=[6, -4, 3])
        kb.add_alias(alias="Russ Cochran", entities=["Q2146908"], probabilities=[0.8])
        return kb

    nlp_1 = English()
    nlp_1.add_pipe("ner")
    entity_linker_1 = nlp_1.add_pipe("entity_linker", last=True)
    entity_linker_1.set_kb(create_kb)
    assert nlp_1.pipe_names == ["ner", "entity_linker"]
    assert entity_linker_1.kb.contains_alias("Russ Cochran")

    data = pickle.dumps(nlp_1)
    nlp_2 = pickle.loads(data)
    assert nlp_2.pipe_names == ["ner", "entity_linker"]
    entity_linker_2 = nlp_2.get_pipe("entity_linker")
    assert entity_linker_2.kb.contains_alias("Russ Cochran")


def test_kb_to_bytes():
    # Test that the KB's to_bytes method works correctly
    nlp = English()
    kb_1 = KnowledgeBase(nlp.vocab, entity_vector_length=3)
    kb_1.add_entity(entity="Q2146908", freq=12, entity_vector=[6, -4, 3])
    kb_1.add_entity(entity="Q66", freq=9, entity_vector=[1, 2, 3])
    kb_1.add_alias(alias="Russ Cochran", entities=["Q2146908"], probabilities=[0.8])
    kb_1.add_alias(alias="Boeing", entities=["Q66"], probabilities=[0.5])
    kb_1.add_alias(
        alias="Randomness", entities=["Q66", "Q2146908"], probabilities=[0.1, 0.2]
    )
    assert kb_1.contains_alias("Russ Cochran")
    kb_bytes = kb_1.to_bytes()
    kb_2 = KnowledgeBase(nlp.vocab, entity_vector_length=3)
    assert not kb_2.contains_alias("Russ Cochran")
    kb_2 = kb_2.from_bytes(kb_bytes)
    # check that both KBs are exactly the same
    assert kb_1.get_size_entities() == kb_2.get_size_entities()
    assert kb_1.entity_vector_length == kb_2.entity_vector_length
    assert kb_1.get_entity_strings() == kb_2.get_entity_strings()
    assert kb_1.get_vector("Q2146908") == kb_2.get_vector("Q2146908")
    assert kb_1.get_vector("Q66") == kb_2.get_vector("Q66")
    assert kb_2.contains_alias("Russ Cochran")
    assert kb_1.get_size_aliases() == kb_2.get_size_aliases()
    assert kb_1.get_alias_strings() == kb_2.get_alias_strings()
    assert len(kb_1.get_alias_candidates("Russ Cochran")) == len(
        kb_2.get_alias_candidates("Russ Cochran")
    )
    assert len(kb_1.get_alias_candidates("Randomness")) == len(
        kb_2.get_alias_candidates("Randomness")
    )


def test_nel_to_bytes():
    # Test that a pipeline with an EL component can be converted to bytes
    def create_kb(vocab):
        kb = KnowledgeBase(vocab, entity_vector_length=3)
        kb.add_entity(entity="Q2146908", freq=12, entity_vector=[6, -4, 3])
        kb.add_alias(alias="Russ Cochran", entities=["Q2146908"], probabilities=[0.8])
        return kb

    nlp_1 = English()
    nlp_1.add_pipe("ner")
    entity_linker_1 = nlp_1.add_pipe("entity_linker", last=True)
    entity_linker_1.set_kb(create_kb)
    assert entity_linker_1.kb.contains_alias("Russ Cochran")
    assert nlp_1.pipe_names == ["ner", "entity_linker"]

    nlp_bytes = nlp_1.to_bytes()
    nlp_2 = English()
    nlp_2.add_pipe("ner")
    nlp_2.add_pipe("entity_linker", last=True)
    assert nlp_2.pipe_names == ["ner", "entity_linker"]
    assert not nlp_2.get_pipe("entity_linker").kb.contains_alias("Russ Cochran")
    nlp_2 = nlp_2.from_bytes(nlp_bytes)
    kb_2 = nlp_2.get_pipe("entity_linker").kb
    assert kb_2.contains_alias("Russ Cochran")
    assert kb_2.get_vector("Q2146908") == [6, -4, 3]
    assert_almost_equal(
        kb_2.get_prior_prob(entity="Q2146908", alias="Russ Cochran"), 0.8
    )


def test_scorer_links():
    train_examples = []
    nlp = English()
    ref1 = nlp("Julia lives in London happily.")
    ref1.ents = [
        Span(ref1, 0, 1, label="PERSON", kb_id="Q2"),
        Span(ref1, 3, 4, label="LOC", kb_id="Q3"),
    ]
    pred1 = nlp("Julia lives in London happily.")
    pred1.ents = [
        Span(pred1, 0, 1, label="PERSON", kb_id="Q70"),
        Span(pred1, 3, 4, label="LOC", kb_id="Q3"),
    ]
    train_examples.append(Example(pred1, ref1))

    ref2 = nlp("She loves London.")
    ref2.ents = [
        Span(ref2, 0, 1, label="PERSON", kb_id="Q2"),
        Span(ref2, 2, 3, label="LOC", kb_id="Q13"),
    ]
    pred2 = nlp("She loves London.")
    pred2.ents = [
        Span(pred2, 0, 1, label="PERSON", kb_id="Q2"),
        Span(pred2, 2, 3, label="LOC", kb_id="NIL"),
    ]
    train_examples.append(Example(pred2, ref2))

    ref3 = nlp("London is great.")
    ref3.ents = [Span(ref3, 0, 1, label="LOC", kb_id="NIL")]
    pred3 = nlp("London is great.")
    pred3.ents = [Span(pred3, 0, 1, label="LOC", kb_id="NIL")]
    train_examples.append(Example(pred3, ref3))

    scores = Scorer().score_links(train_examples, negative_labels=["NIL"])
    assert scores["nel_f_per_type"]["PERSON"]["p"] == 1 / 2
    assert scores["nel_f_per_type"]["PERSON"]["r"] == 1 / 2
    assert scores["nel_f_per_type"]["LOC"]["p"] == 1 / 1
    assert scores["nel_f_per_type"]["LOC"]["r"] == 1 / 2

    assert scores["nel_micro_p"] == 2 / 3
    assert scores["nel_micro_r"] == 2 / 4
