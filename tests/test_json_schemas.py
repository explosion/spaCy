# coding: utf-8
from __future__ import unicode_literals

from spacy.util import get_json_validator, validate_json, validate_schema
from spacy.cli._schemas import META_SCHEMA, TRAINING_SCHEMA
from spacy.matcher._schemas import TOKEN_PATTERN_SCHEMA
import pytest


@pytest.fixture(scope="session")
def training_schema_validator():
    return get_json_validator(TRAINING_SCHEMA)


def test_validate_schema():
    validate_schema({"type": "object"})
    with pytest.raises(Exception):
        validate_schema({"type": lambda x: x})


@pytest.mark.parametrize("schema", [TRAINING_SCHEMA, META_SCHEMA, TOKEN_PATTERN_SCHEMA])
def test_schemas(schema):
    validate_schema(schema)


@pytest.mark.parametrize(
    "data",
    [
        {"text": "Hello world"},
        {"text": "Hello", "ents": [{"start": 0, "end": 5, "label": "TEST"}]},
    ],
)
def test_json_schema_training_valid(data, training_schema_validator):
    errors = validate_json([data], training_schema_validator)
    assert not errors


@pytest.mark.parametrize(
    "data,n_errors",
    [
        ({"spans": []}, 1),
        ({"text": "Hello", "ents": [{"start": "0", "end": "5", "label": "TEST"}]}, 2),
        ({"text": "Hello", "ents": [{"start": 0, "end": 5}]}, 1),
        ({"text": "Hello", "ents": [{"start": 0, "end": 5, "label": "test"}]}, 1),
        ({"text": "spaCy", "tokens": [{"pos": "PROPN"}]}, 2),
    ],
)
def test_json_schema_training_invalid(data, n_errors, training_schema_validator):
    errors = validate_json([data], training_schema_validator)
    assert len(errors) == n_errors
