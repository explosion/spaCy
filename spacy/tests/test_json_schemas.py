# coding: utf-8
from __future__ import unicode_literals

from spacy.cli.schemas import validate_json, get_schema
import pytest


@pytest.fixture(scope="session")
def training_schema():
    return get_schema("training")


def test_json_schema_get():
    schema = get_schema("training")
    assert schema
    with pytest.raises(ValueError):
        schema = get_schema("xxx")


@pytest.mark.parametrize(
    "data",
    [
        {"text": "Hello world"},
        {"text": "Hello", "ents": [{"start": 0, "end": 5, "label": "TEST"}]},
    ],
)
def test_json_schema_training_valid(data, training_schema):
    errors = validate_json([data], training_schema)
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
def test_json_schema_training_invalid(data, n_errors, training_schema):
    errors = validate_json([data], training_schema)
    assert len(errors) == n_errors
