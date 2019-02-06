# coding: utf-8
from __future__ import unicode_literals

from spacy.util import validate_json, validate_schema
from spacy.cli._schemas import META_SCHEMA, TRAINING_SCHEMA
import pytest


def test_validate_schema():
    validate_schema({"type": "object"})
    with pytest.raises(Exception):
        validate_schema({"type": lambda x: x})


@pytest.mark.parametrize("schema", [TRAINING_SCHEMA, META_SCHEMA])
def test_schemas(schema):
    validate_schema(schema)


@pytest.mark.parametrize(
    "data",
    [
        {"text": "Hello world"},
        {"text": "Hello", "ents": [{"start": 0, "end": 5, "label": "TEST"}]},
    ],
)
def test_json_schema_training_valid(data):
    errors = validate_json([data], TRAINING_SCHEMA)
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
def test_json_schema_training_invalid(data, n_errors):
    errors = validate_json([data], TRAINING_SCHEMA)
    assert len(errors) == n_errors
