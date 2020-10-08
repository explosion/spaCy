import pytest

from spacy import registry
from spacy.tokens import Span
from spacy.language import Language
from spacy.pipeline import EntityRuler
from spacy.errors import MatchPatternError


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


def test_entity_ruler_init(nlp, patterns):
    ruler = EntityRuler(nlp, patterns=patterns)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    assert "HELLO" in ruler
    assert "BYE" in ruler
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(patterns)
    doc = nlp("hello world bye bye")
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "HELLO"
    assert doc.ents[1].label_ == "BYE"


def test_entity_ruler_init_patterns(nlp, patterns):
    # initialize with patterns
    ruler = nlp.add_pipe("entity_ruler")
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
    ruler = nlp.add_pipe("entity_ruler")
    assert len(ruler.labels) == 0
    nlp.initialize()
    assert len(ruler.labels) == 4
    doc = nlp("hello world bye bye")
    assert doc.ents[0].label_ == "HELLO"
    assert doc.ents[1].label_ == "BYE"


def test_entity_ruler_init_clear(nlp, patterns):
    """Test that initialization clears patterns."""
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(patterns)
    assert len(ruler.labels) == 4
    ruler.initialize(lambda: [])
    assert len(ruler.labels) == 0


def test_entity_ruler_existing(nlp, patterns):
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(patterns)
    nlp.add_pipe("add_ent", before="entity_ruler")
    doc = nlp("OH HELLO WORLD bye bye")
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "ORG"
    assert doc.ents[1].label_ == "BYE"


def test_entity_ruler_existing_overwrite(nlp, patterns):
    ruler = nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})
    ruler.add_patterns(patterns)
    nlp.add_pipe("add_ent", before="entity_ruler")
    doc = nlp("OH HELLO WORLD bye bye")
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "HELLO"
    assert doc.ents[0].text == "HELLO"
    assert doc.ents[1].label_ == "BYE"


def test_entity_ruler_existing_complex(nlp, patterns):
    ruler = nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})
    ruler.add_patterns(patterns)
    nlp.add_pipe("add_ent", before="entity_ruler")
    doc = nlp("foo foo bye bye")
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "COMPLEX"
    assert doc.ents[1].label_ == "BYE"
    assert len(doc.ents[0]) == 2
    assert len(doc.ents[1]) == 2


def test_entity_ruler_entity_id(nlp, patterns):
    ruler = nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})
    ruler.add_patterns(patterns)
    doc = nlp("Apple is a technology company")
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "TECH_ORG"
    assert doc.ents[0].ent_id_ == "a1"


def test_entity_ruler_cfg_ent_id_sep(nlp, patterns):
    config = {"overwrite_ents": True, "ent_id_sep": "**"}
    ruler = nlp.add_pipe("entity_ruler", config=config)
    ruler.add_patterns(patterns)
    assert "TECH_ORG**a1" in ruler.phrase_patterns
    doc = nlp("Apple is a technology company")
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "TECH_ORG"
    assert doc.ents[0].ent_id_ == "a1"


def test_entity_ruler_serialize_bytes(nlp, patterns):
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


def test_entity_ruler_serialize_phrase_matcher_attr_bytes(nlp, patterns):
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


def test_entity_ruler_validate(nlp):
    ruler = EntityRuler(nlp)
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


def test_entity_ruler_properties(nlp, patterns):
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    assert sorted(ruler.labels) == sorted(["HELLO", "BYE", "COMPLEX", "TECH_ORG"])
    assert sorted(ruler.ent_ids) == ["a1", "a2"]


def test_entity_ruler_overlapping_spans(nlp):
    ruler = EntityRuler(nlp)
    patterns = [
        {"label": "FOOBAR", "pattern": "foo bar"},
        {"label": "BARBAZ", "pattern": "bar baz"},
    ]
    ruler.add_patterns(patterns)
    doc = ruler(nlp.make_doc("foo bar baz"))
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "FOOBAR"
