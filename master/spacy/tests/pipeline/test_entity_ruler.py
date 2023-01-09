import pytest

from spacy import registry
from spacy.tokens import Doc, Span
from spacy.language import Language
from spacy.lang.en import English
from spacy.pipeline import EntityRuler, EntityRecognizer, merge_entities
from spacy.pipeline import SpanRuler
from spacy.pipeline.ner import DEFAULT_NER_MODEL
from spacy.errors import MatchPatternError
from spacy.tests.util import make_tempdir

from thinc.api import NumpyOps, get_current_ops

ENTITY_RULERS = ["entity_ruler", "future_entity_ruler"]


@pytest.fixture
def nlp():
    return Language()


@pytest.fixture
@registry.misc("entity_ruler_patterns")
def patterns():
    return [
        {"label": "HELLO", "pattern": "hello world"},
        {"label": "BYE", "pattern": [{"LOWER": "bye"}, {"LOWER": "bye"}]},
        {"label": "HELLO", "pattern": [{"ORTH": "HELLO"}]},
        {"label": "COMPLEX", "pattern": [{"ORTH": "foo", "OP": "*"}]},
        {"label": "TECH_ORG", "pattern": "Apple", "id": "a1"},
        {"label": "TECH_ORG", "pattern": "Microsoft", "id": "a2"},
    ]


@Language.component("add_ent")
def add_ent_component(doc):
    doc.ents = [Span(doc, 0, 3, label="ORG")]
    return doc


@pytest.mark.issue(3345)
@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_issue3345(entity_ruler_factory):
    """Test case where preset entity crosses sentence boundary."""
    nlp = English()
    doc = Doc(nlp.vocab, words=["I", "live", "in", "New", "York"])
    doc[4].is_sent_start = True
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    ruler.add_patterns([{"label": "GPE", "pattern": "New York"}])
    cfg = {"model": DEFAULT_NER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    ner = EntityRecognizer(doc.vocab, model)
    # Add the OUT action. I wouldn't have thought this would be necessary...
    ner.moves.add_action(5, "")
    ner.add_label("GPE")
    doc = ruler(doc)
    # Get into the state just before "New"
    state = ner.moves.init_batch([doc])[0]
    ner.moves.apply_transition(state, "O")
    ner.moves.apply_transition(state, "O")
    ner.moves.apply_transition(state, "O")
    # Check that B-GPE is valid.
    assert ner.moves.is_valid(state, "B-GPE")


@pytest.mark.issue(4849)
@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_issue4849(entity_ruler_factory):
    nlp = English()
    patterns = [
        {"label": "PERSON", "pattern": "joe biden", "id": "joe-biden"},
        {"label": "PERSON", "pattern": "bernie sanders", "id": "bernie-sanders"},
    ]
    ruler = nlp.add_pipe(
        entity_ruler_factory,
        name="entity_ruler",
        config={"phrase_matcher_attr": "LOWER"},
    )
    ruler.add_patterns(patterns)
    text = """
    The left is starting to take aim at Democratic front-runner Joe Biden.
    Sen. Bernie Sanders joined in her criticism: "There is no 'middle ground' when it comes to climate policy."
    """
    # USING 1 PROCESS
    count_ents = 0
    for doc in nlp.pipe([text], n_process=1):
        count_ents += len([ent for ent in doc.ents if ent.ent_id > 0])
    assert count_ents == 2
    # USING 2 PROCESSES
    if isinstance(get_current_ops, NumpyOps):
        count_ents = 0
        for doc in nlp.pipe([text], n_process=2):
            count_ents += len([ent for ent in doc.ents if ent.ent_id > 0])
        assert count_ents == 2


@pytest.mark.issue(5918)
@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_issue5918(entity_ruler_factory):
    # Test edge case when merging entities.
    nlp = English()
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    patterns = [
        {"label": "ORG", "pattern": "Digicon Inc"},
        {"label": "ORG", "pattern": "Rotan Mosle Inc's"},
        {"label": "ORG", "pattern": "Rotan Mosle Technology Partners Ltd"},
    ]
    ruler.add_patterns(patterns)

    text = """
        Digicon Inc said it has completed the previously-announced disposition
        of its computer systems division to an investment group led by
        Rotan Mosle Inc's Rotan Mosle Technology Partners Ltd affiliate.
        """
    doc = nlp(text)
    assert len(doc.ents) == 3
    # make it so that the third span's head is within the entity (ent_iob=I)
    # bug #5918 would wrongly transfer that I to the full entity, resulting in 2 instead of 3 final ents.
    # TODO: test for logging here
    # with pytest.warns(UserWarning):
    #     doc[29].head = doc[33]
    doc = merge_entities(doc)
    assert len(doc.ents) == 3


@pytest.mark.issue(8168)
@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_issue8168(entity_ruler_factory):
    nlp = English()
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    patterns = [
        {"label": "ORG", "pattern": "Apple"},
        {
            "label": "GPE",
            "pattern": [{"LOWER": "san"}, {"LOWER": "francisco"}],
            "id": "san-francisco",
        },
        {
            "label": "GPE",
            "pattern": [{"LOWER": "san"}, {"LOWER": "fran"}],
            "id": "san-francisco",
        },
    ]
    ruler.add_patterns(patterns)
    doc = nlp("San Francisco San Fran")
    assert all(t.ent_id_ == "san-francisco" for t in doc)


@pytest.mark.issue(8216)
@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_fix8216(nlp, patterns, entity_ruler_factory):
    """Test that patterns don't get added excessively."""
    ruler = nlp.add_pipe(
        entity_ruler_factory, name="entity_ruler", config={"validate": True}
    )
    ruler.add_patterns(patterns)
    pattern_count = sum(len(mm) for mm in ruler.matcher._patterns.values())
    assert pattern_count > 0
    ruler.add_patterns([])
    after_count = sum(len(mm) for mm in ruler.matcher._patterns.values())
    assert after_count == pattern_count


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_init(nlp, patterns, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    ruler.add_patterns(patterns)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    assert "HELLO" in ruler
    assert "BYE" in ruler
    nlp.remove_pipe("entity_ruler")
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    ruler.add_patterns(patterns)
    doc = nlp("hello world bye bye")
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "HELLO"
    assert doc.ents[1].label_ == "BYE"


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_no_patterns_warns(nlp, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    assert len(ruler) == 0
    assert len(ruler.labels) == 0
    nlp.remove_pipe("entity_ruler")
    nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    assert nlp.pipe_names == ["entity_ruler"]
    with pytest.warns(UserWarning):
        doc = nlp("hello world bye bye")
    assert len(doc.ents) == 0


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_init_patterns(nlp, patterns, entity_ruler_factory):
    # initialize with patterns
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    assert len(ruler.labels) == 0
    ruler.initialize(lambda: [], patterns=patterns)
    assert len(ruler.labels) == 4
    doc = nlp("hello world bye bye")
    assert doc.ents[0].label_ == "HELLO"
    assert doc.ents[1].label_ == "BYE"
    nlp.remove_pipe("entity_ruler")
    # initialize with patterns from misc registry
    nlp.config["initialize"]["components"]["entity_ruler"] = {
        "patterns": {"@misc": "entity_ruler_patterns"}
    }
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    assert len(ruler.labels) == 0
    nlp.initialize()
    assert len(ruler.labels) == 4
    doc = nlp("hello world bye bye")
    assert doc.ents[0].label_ == "HELLO"
    assert doc.ents[1].label_ == "BYE"


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_init_clear(nlp, patterns, entity_ruler_factory):
    """Test that initialization clears patterns."""
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    ruler.add_patterns(patterns)
    assert len(ruler.labels) == 4
    ruler.initialize(lambda: [])
    assert len(ruler.labels) == 0


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_clear(nlp, patterns, entity_ruler_factory):
    """Test that initialization clears patterns."""
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    ruler.add_patterns(patterns)
    assert len(ruler.labels) == 4
    doc = nlp("hello world")
    assert len(doc.ents) == 1
    ruler.clear()
    assert len(ruler.labels) == 0
    with pytest.warns(UserWarning):
        doc = nlp("hello world")
    assert len(doc.ents) == 0


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_existing(nlp, patterns, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    ruler.add_patterns(patterns)
    nlp.add_pipe("add_ent", before="entity_ruler")
    doc = nlp("OH HELLO WORLD bye bye")
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "ORG"
    assert doc.ents[1].label_ == "BYE"


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_existing_overwrite(nlp, patterns, entity_ruler_factory):
    ruler = nlp.add_pipe(
        entity_ruler_factory, name="entity_ruler", config={"overwrite_ents": True}
    )
    ruler.add_patterns(patterns)
    nlp.add_pipe("add_ent", before="entity_ruler")
    doc = nlp("OH HELLO WORLD bye bye")
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "HELLO"
    assert doc.ents[0].text == "HELLO"
    assert doc.ents[1].label_ == "BYE"


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_existing_complex(nlp, patterns, entity_ruler_factory):
    ruler = nlp.add_pipe(
        entity_ruler_factory, name="entity_ruler", config={"overwrite_ents": True}
    )
    ruler.add_patterns(patterns)
    nlp.add_pipe("add_ent", before="entity_ruler")
    doc = nlp("foo foo bye bye")
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "COMPLEX"
    assert doc.ents[1].label_ == "BYE"
    assert len(doc.ents[0]) == 2
    assert len(doc.ents[1]) == 2


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_entity_id(nlp, patterns, entity_ruler_factory):
    ruler = nlp.add_pipe(
        entity_ruler_factory, name="entity_ruler", config={"overwrite_ents": True}
    )
    ruler.add_patterns(patterns)
    doc = nlp("Apple is a technology company")
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "TECH_ORG"
    assert doc.ents[0].ent_id_ == "a1"


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_cfg_ent_id_sep(nlp, patterns, entity_ruler_factory):
    config = {"overwrite_ents": True, "ent_id_sep": "**"}
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler", config=config)
    ruler.add_patterns(patterns)
    doc = nlp("Apple is a technology company")
    if isinstance(ruler, EntityRuler):
        assert "TECH_ORG**a1" in ruler.phrase_patterns
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "TECH_ORG"
    assert doc.ents[0].ent_id_ == "a1"


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_serialize_bytes(nlp, patterns, entity_ruler_factory):
    ruler = EntityRuler(nlp, patterns=patterns)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    ruler_bytes = ruler.to_bytes()
    new_ruler = EntityRuler(nlp)
    assert len(new_ruler) == 0
    assert len(new_ruler.labels) == 0
    new_ruler = new_ruler.from_bytes(ruler_bytes)
    assert len(new_ruler) == len(patterns)
    assert len(new_ruler.labels) == 4
    assert len(new_ruler.patterns) == len(ruler.patterns)
    for pattern in ruler.patterns:
        assert pattern in new_ruler.patterns
    assert sorted(new_ruler.labels) == sorted(ruler.labels)


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_serialize_phrase_matcher_attr_bytes(
    nlp, patterns, entity_ruler_factory
):
    ruler = EntityRuler(nlp, phrase_matcher_attr="LOWER", patterns=patterns)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    ruler_bytes = ruler.to_bytes()
    new_ruler = EntityRuler(nlp)
    assert len(new_ruler) == 0
    assert len(new_ruler.labels) == 0
    assert new_ruler.phrase_matcher_attr is None
    new_ruler = new_ruler.from_bytes(ruler_bytes)
    assert len(new_ruler) == len(patterns)
    assert len(new_ruler.labels) == 4
    assert new_ruler.phrase_matcher_attr == "LOWER"


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_validate(nlp, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    validated_ruler = EntityRuler(nlp, validate=True)

    valid_pattern = {"label": "HELLO", "pattern": [{"LOWER": "HELLO"}]}
    invalid_pattern = {"label": "HELLO", "pattern": [{"ASDF": "HELLO"}]}

    # invalid pattern raises error without validate
    with pytest.raises(ValueError):
        ruler.add_patterns([invalid_pattern])

    # valid pattern is added without errors with validate
    validated_ruler.add_patterns([valid_pattern])

    # invalid pattern raises error with validate
    with pytest.raises(MatchPatternError):
        validated_ruler.add_patterns([invalid_pattern])


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_properties(nlp, patterns, entity_ruler_factory):
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    assert sorted(ruler.labels) == sorted(["HELLO", "BYE", "COMPLEX", "TECH_ORG"])
    assert sorted(ruler.ent_ids) == ["a1", "a2"]


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_overlapping_spans(nlp, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    patterns = [
        {"label": "FOOBAR", "pattern": "foo bar"},
        {"label": "BARBAZ", "pattern": "bar baz"},
    ]
    ruler.add_patterns(patterns)
    doc = nlp("foo bar baz")
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "FOOBAR"


@pytest.mark.parametrize("n_process", [1, 2])
@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_multiprocessing(nlp, n_process, entity_ruler_factory):
    if isinstance(get_current_ops, NumpyOps) or n_process < 2:
        texts = ["I enjoy eating Pizza Hut pizza."]

        patterns = [{"label": "FASTFOOD", "pattern": "Pizza Hut", "id": "1234"}]

        ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
        ruler.add_patterns(patterns)

        for doc in nlp.pipe(texts, n_process=2):
            for ent in doc.ents:
                assert ent.ent_id_ == "1234"


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_serialize_jsonl(nlp, patterns, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    ruler.add_patterns(patterns)
    with make_tempdir() as d:
        ruler.to_disk(d / "test_ruler.jsonl")
        ruler.from_disk(d / "test_ruler.jsonl")  # read from an existing jsonl file
        with pytest.raises(ValueError):
            ruler.from_disk(d / "non_existing.jsonl")  # read from a bad jsonl file


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_serialize_dir(nlp, patterns, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    ruler.add_patterns(patterns)
    with make_tempdir() as d:
        ruler.to_disk(d / "test_ruler")
        ruler.from_disk(d / "test_ruler")  # read from an existing directory
        with pytest.raises(ValueError):
            ruler.from_disk(d / "non_existing_dir")  # read from a bad directory


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_remove_basic(nlp, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    patterns = [
        {"label": "PERSON", "pattern": "Dina", "id": "dina"},
        {"label": "ORG", "pattern": "ACME", "id": "acme"},
        {"label": "ORG", "pattern": "ACM"},
    ]
    ruler.add_patterns(patterns)
    doc = nlp("Dina went to school")
    assert len(ruler.patterns) == 3
    assert len(doc.ents) == 1
    if isinstance(ruler, EntityRuler):
        assert "PERSON||dina" in ruler.phrase_matcher
    assert doc.ents[0].label_ == "PERSON"
    assert doc.ents[0].text == "Dina"
    if isinstance(ruler, EntityRuler):
        ruler.remove("dina")
    else:
        ruler.remove_by_id("dina")
    doc = nlp("Dina went to school")
    assert len(doc.ents) == 0
    if isinstance(ruler, EntityRuler):
        assert "PERSON||dina" not in ruler.phrase_matcher
    assert len(ruler.patterns) == 2


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_remove_same_id_multiple_patterns(nlp, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    patterns = [
        {"label": "PERSON", "pattern": "Dina", "id": "dina"},
        {"label": "ORG", "pattern": "DinaCorp", "id": "dina"},
        {"label": "ORG", "pattern": "ACME", "id": "acme"},
    ]
    ruler.add_patterns(patterns)
    doc = nlp("Dina founded DinaCorp and ACME.")
    assert len(ruler.patterns) == 3
    if isinstance(ruler, EntityRuler):
        assert "PERSON||dina" in ruler.phrase_matcher
        assert "ORG||dina" in ruler.phrase_matcher
    assert len(doc.ents) == 3
    if isinstance(ruler, EntityRuler):
        ruler.remove("dina")
    else:
        ruler.remove_by_id("dina")
    doc = nlp("Dina founded DinaCorp and ACME.")
    assert len(ruler.patterns) == 1
    if isinstance(ruler, EntityRuler):
        assert "PERSON||dina" not in ruler.phrase_matcher
        assert "ORG||dina" not in ruler.phrase_matcher
    assert len(doc.ents) == 1


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_remove_nonexisting_pattern(nlp, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    patterns = [
        {"label": "PERSON", "pattern": "Dina", "id": "dina"},
        {"label": "ORG", "pattern": "ACME", "id": "acme"},
        {"label": "ORG", "pattern": "ACM"},
    ]
    ruler.add_patterns(patterns)
    assert len(ruler.patterns) == 3
    with pytest.raises(ValueError):
        ruler.remove("nepattern")
    if isinstance(ruler, SpanRuler):
        with pytest.raises(ValueError):
            ruler.remove_by_id("nepattern")


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_remove_several_patterns(nlp, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    patterns = [
        {"label": "PERSON", "pattern": "Dina", "id": "dina"},
        {"label": "ORG", "pattern": "ACME", "id": "acme"},
        {"label": "ORG", "pattern": "ACM"},
    ]
    ruler.add_patterns(patterns)
    doc = nlp("Dina founded her company ACME.")
    assert len(ruler.patterns) == 3
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "PERSON"
    assert doc.ents[0].text == "Dina"
    assert doc.ents[1].label_ == "ORG"
    assert doc.ents[1].text == "ACME"
    if isinstance(ruler, EntityRuler):
        ruler.remove("dina")
    else:
        ruler.remove_by_id("dina")
    doc = nlp("Dina founded her company ACME")
    assert len(ruler.patterns) == 2
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "ORG"
    assert doc.ents[0].text == "ACME"
    if isinstance(ruler, EntityRuler):
        ruler.remove("acme")
    else:
        ruler.remove_by_id("acme")
    doc = nlp("Dina founded her company ACME")
    assert len(ruler.patterns) == 1
    assert len(doc.ents) == 0


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_remove_patterns_in_a_row(nlp, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    patterns = [
        {"label": "PERSON", "pattern": "Dina", "id": "dina"},
        {"label": "ORG", "pattern": "ACME", "id": "acme"},
        {"label": "DATE", "pattern": "her birthday", "id": "bday"},
        {"label": "ORG", "pattern": "ACM"},
    ]
    ruler.add_patterns(patterns)
    doc = nlp("Dina founded her company ACME on her birthday")
    assert len(doc.ents) == 3
    assert doc.ents[0].label_ == "PERSON"
    assert doc.ents[0].text == "Dina"
    assert doc.ents[1].label_ == "ORG"
    assert doc.ents[1].text == "ACME"
    assert doc.ents[2].label_ == "DATE"
    assert doc.ents[2].text == "her birthday"
    if isinstance(ruler, EntityRuler):
        ruler.remove("dina")
        ruler.remove("acme")
        ruler.remove("bday")
    else:
        ruler.remove_by_id("dina")
        ruler.remove_by_id("acme")
        ruler.remove_by_id("bday")
    doc = nlp("Dina went to school")
    assert len(doc.ents) == 0


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_remove_all_patterns(nlp, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    patterns = [
        {"label": "PERSON", "pattern": "Dina", "id": "dina"},
        {"label": "ORG", "pattern": "ACME", "id": "acme"},
        {"label": "DATE", "pattern": "her birthday", "id": "bday"},
    ]
    ruler.add_patterns(patterns)
    assert len(ruler.patterns) == 3
    if isinstance(ruler, EntityRuler):
        ruler.remove("dina")
    else:
        ruler.remove_by_id("dina")
    assert len(ruler.patterns) == 2
    if isinstance(ruler, EntityRuler):
        ruler.remove("acme")
    else:
        ruler.remove_by_id("acme")
    assert len(ruler.patterns) == 1
    if isinstance(ruler, EntityRuler):
        ruler.remove("bday")
    else:
        ruler.remove_by_id("bday")
    assert len(ruler.patterns) == 0
    with pytest.warns(UserWarning):
        doc = nlp("Dina founded her company ACME on her birthday")
        assert len(doc.ents) == 0


@pytest.mark.parametrize("entity_ruler_factory", ENTITY_RULERS)
def test_entity_ruler_remove_and_add(nlp, entity_ruler_factory):
    ruler = nlp.add_pipe(entity_ruler_factory, name="entity_ruler")
    patterns = [{"label": "DATE", "pattern": "last time"}]
    ruler.add_patterns(patterns)
    doc = ruler(
        nlp.make_doc("I saw him last time we met, this time he brought some flowers")
    )
    assert len(ruler.patterns) == 1
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "DATE"
    assert doc.ents[0].text == "last time"
    patterns1 = [{"label": "DATE", "pattern": "this time", "id": "ttime"}]
    ruler.add_patterns(patterns1)
    doc = ruler(
        nlp.make_doc("I saw him last time we met, this time he brought some flowers")
    )
    assert len(ruler.patterns) == 2
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "DATE"
    assert doc.ents[0].text == "last time"
    assert doc.ents[1].label_ == "DATE"
    assert doc.ents[1].text == "this time"
    if isinstance(ruler, EntityRuler):
        ruler.remove("ttime")
    else:
        ruler.remove_by_id("ttime")
    doc = ruler(
        nlp.make_doc("I saw him last time we met, this time he brought some flowers")
    )
    assert len(ruler.patterns) == 1
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "DATE"
    assert doc.ents[0].text == "last time"
    ruler.add_patterns(patterns1)
    doc = ruler(
        nlp.make_doc("I saw him last time we met, this time he brought some flowers")
    )
    assert len(ruler.patterns) == 2
    assert len(doc.ents) == 2
    patterns2 = [{"label": "DATE", "pattern": "another time", "id": "ttime"}]
    ruler.add_patterns(patterns2)
    doc = ruler(
        nlp.make_doc(
            "I saw him last time we met, this time he brought some flowers, another time some chocolate."
        )
    )
    assert len(ruler.patterns) == 3
    assert len(doc.ents) == 3
    if isinstance(ruler, EntityRuler):
        ruler.remove("ttime")
    else:
        ruler.remove_by_id("ttime")
    doc = ruler(
        nlp.make_doc(
            "I saw him last time we met, this time he brought some flowers, another time some chocolate."
        )
    )
    assert len(ruler.patterns) == 1
    assert len(doc.ents) == 1
