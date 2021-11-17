import pytest

from spacy import registry
from spacy.tokens import Span
from spacy.language import Language
from spacy.pipeline import EntityRuler
from spacy.errors import MatchPatternError
from thinc.api import NumpyOps, get_current_ops


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


def test_entity_ruler_no_patterns_warns(nlp):
    ruler = EntityRuler(nlp)
    assert len(ruler) == 0
    assert len(ruler.labels) == 0
    nlp.add_pipe("entity_ruler")
    assert nlp.pipe_names == ["entity_ruler"]
    with pytest.warns(UserWarning):
        doc = nlp("hello world bye bye")
    assert len(doc.ents) == 0


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


def test_entity_ruler_clear(nlp, patterns):
    """Test that initialization clears patterns."""
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(patterns)
    assert len(ruler.labels) == 4
    doc = nlp("hello world")
    assert len(doc.ents) == 1
    ruler.clear()
    assert len(ruler.labels) == 0
    with pytest.warns(UserWarning):
        doc = nlp("hello world")
    assert len(doc.ents) == 0


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


@pytest.mark.parametrize("n_process", [1, 2])
def test_entity_ruler_multiprocessing(nlp, n_process):
    if isinstance(get_current_ops, NumpyOps) or n_process < 2:
        texts = ["I enjoy eating Pizza Hut pizza."]

        patterns = [{"label": "FASTFOOD", "pattern": "Pizza Hut", "id": "1234"}]

        ruler = nlp.add_pipe("entity_ruler")
        ruler.add_patterns(patterns)

        for doc in nlp.pipe(texts, n_process=2):
            for ent in doc.ents:
                assert ent.ent_id_ == "1234"


def test_entity_ruler_remove_basic(nlp):
    ruler = EntityRuler(nlp)
    patterns = [
        {"label": "PERSON", "pattern": "Duygu", "id": "duygu"},
        {"label": "ORG", "pattern": "ACME", "id": "acme"},
        {"label": "ORG", "pattern": "ACM"},
    ]
    ruler.add_patterns(patterns)
    doc = ruler(nlp.make_doc("Duygu went to school"))
    assert len(ruler.patterns) == 3
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "PERSON"
    assert doc.ents[0].text == "Duygu"
    assert "PERSON||duygu" in ruler.phrase_matcher
    ruler.remove("duygu")
    doc = ruler(nlp.make_doc("Duygu went to school"))
    assert len(doc.ents) == 0
    assert "PERSON||duygu" not in ruler.phrase_matcher
    assert len(ruler.patterns) == 2


def test_entity_ruler_remove_same_id_multiple_patterns(nlp):
    ruler = EntityRuler(nlp)
    patterns = [
        {"label": "PERSON", "pattern": "Duygu", "id": "duygu"},
        {"label": "ORG", "pattern": "DuyguCorp", "id": "duygu"},
        {"label": "ORG", "pattern": "ACME", "id": "acme"},
    ]
    ruler.add_patterns(patterns)
    doc = ruler(nlp.make_doc("Duygu founded DuyguCorp and ACME."))
    assert len(ruler.patterns) == 3
    assert "PERSON||duygu" in ruler.phrase_matcher
    assert "ORG||duygu" in ruler.phrase_matcher
    assert len(doc.ents) == 3
    ruler.remove("duygu")
    doc = ruler(nlp.make_doc("Duygu founded DuyguCorp and ACME."))
    assert len(ruler.patterns) == 1
    assert "PERSON||duygu" not in ruler.phrase_matcher
    assert "ORG||duygu" not in ruler.phrase_matcher
    assert len(doc.ents) == 1


def test_entity_ruler_remove_nonexisting_pattern(nlp):
    ruler = EntityRuler(nlp)
    patterns = [
        {"label": "PERSON", "pattern": "Duygu", "id": "duygu"},
        {"label": "ORG", "pattern": "ACME", "id": "acme"},
        {"label": "ORG", "pattern": "ACM"},
    ]
    ruler.add_patterns(patterns)
    assert len(ruler.patterns) == 3
    with pytest.raises(ValueError):
        ruler.remove("nepattern")
        assert len(ruler.patterns) == 3


def test_entity_ruler_remove_several_patterns(nlp):
    ruler = EntityRuler(nlp)
    patterns = [
        {"label": "PERSON", "pattern": "Duygu", "id": "duygu"},
        {"label": "ORG", "pattern": "ACME", "id": "acme"},
        {"label": "ORG", "pattern": "ACM"},
    ]
    ruler.add_patterns(patterns)
    doc = ruler(nlp.make_doc("Duygu founded her company ACME."))
    assert len(ruler.patterns) == 3
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "PERSON"
    assert doc.ents[0].text == "Duygu"
    assert doc.ents[1].label_ == "ORG"
    assert doc.ents[1].text == "ACME"
    ruler.remove("duygu")
    doc = ruler(nlp.make_doc("Duygu founded her company ACME"))
    assert len(ruler.patterns) == 2
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "ORG"
    assert doc.ents[0].text == "ACME"
    ruler.remove("acme")
    doc = ruler(nlp.make_doc("Duygu founded her company ACME"))
    assert len(ruler.patterns) == 1
    assert len(doc.ents) == 0


def test_entity_ruler_remove_patterns_in_a_row(nlp):
    ruler = EntityRuler(nlp)
    patterns = [
        {"label": "PERSON", "pattern": "Duygu", "id": "duygu"},
        {"label": "ORG", "pattern": "ACME", "id": "acme"},
        {"label": "DATE", "pattern": "her birthday", "id": "bday"},
        {"label": "ORG", "pattern": "ACM"},
    ]
    ruler.add_patterns(patterns)
    doc = ruler(nlp.make_doc("Duygu founded her company ACME on her birthday"))
    assert len(doc.ents) == 3
    assert doc.ents[0].label_ == "PERSON"
    assert doc.ents[0].text == "Duygu"
    assert doc.ents[1].label_ == "ORG"
    assert doc.ents[1].text == "ACME"
    assert doc.ents[2].label_ == "DATE"
    assert doc.ents[2].text == "her birthday"
    ruler.remove("duygu")
    ruler.remove("acme")
    ruler.remove("bday")
    doc = ruler(nlp.make_doc("Duygu went to school"))
    assert len(doc.ents) == 0


def test_entity_ruler_remove_all_patterns(nlp):
    ruler = EntityRuler(nlp)
    patterns = [
        {"label": "PERSON", "pattern": "Duygu", "id": "duygu"},
        {"label": "ORG", "pattern": "ACME", "id": "acme"},
        {"label": "DATE", "pattern": "her birthday", "id": "bday"},
    ]
    ruler.add_patterns(patterns)
    assert len(ruler.patterns) == 3
    ruler.remove("duygu")
    assert len(ruler.patterns) == 2
    ruler.remove("acme")
    assert len(ruler.patterns) == 1
    ruler.remove("bday")
    assert len(ruler.patterns) == 0
    with pytest.warns(UserWarning):
        doc = ruler(nlp.make_doc("Duygu founded her company ACME on her birthday"))
        assert len(doc.ents) == 0


def test_entity_ruler_remove_and_add(nlp):
    ruler = EntityRuler(nlp)
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
    ruler.remove("ttime")
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
    ruler.remove("ttime")
    doc = ruler(
        nlp.make_doc(
            "I saw him last time we met, this time he brought some flowers, another time some chocolate."
        )
    )
    assert len(ruler.patterns) == 1
    assert len(doc.ents) == 1
