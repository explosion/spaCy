import pytest

from spacy import registry
from spacy.language import Language


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


def test_entity_ruler_fix8216(nlp, patterns):
    """Test that patterns don't get added excessively."""
    ruler = nlp.add_pipe("entity_ruler", config={"validate": True})
    ruler.add_patterns(patterns)
    pattern_count = sum(len(mm) for mm in ruler.matcher._patterns.values())
    assert pattern_count > 0
    ruler.add_patterns([])
    after_count = sum(len(mm) for mm in ruler.matcher._patterns.values())
    assert after_count == pattern_count
