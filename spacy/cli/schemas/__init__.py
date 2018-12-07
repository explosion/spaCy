# coding: utf-8
from __future__ import unicode_literals

from pathlib import Path
from jsonschema import Draft4Validator
import srsly

from ...errors import Errors


SCHEMAS = {}


def get_schema(name):
    """Get the JSON schema for a given name. Looks for a .json file in
    spacy.cli.schemas, validates the schema and raises ValueError if not found.

    EXAMPLE:
        >>> schema = get_schema('training')

    name (unicode): The name of the schema.
    RETURNS (dict): The JSON schema.
    """
    if name not in SCHEMAS:
        schema_path = Path(__file__).parent / "{}.json".format(name)
        if not schema_path.exists():
            raise ValueError(Errors.E104.format(name=name))
        schema = srsly.read_json(schema_path)
        # TODO: replace with (stable) Draft6Validator, if available
        validator = Draft4Validator(schema)
        validator.check_schema(schema)
        SCHEMAS[name] = schema
    return SCHEMAS[name]


def validate_json(data, schema):
    """Validate data against a given JSON schema (see https://json-schema.org).

    data: JSON-serializable data to validate.
    schema (dict): The JSON schema.
    RETURNS (list): A list of error messages, if available.
    """
    validator = Draft4Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
        if err.path:
            err_path = "[{}]".format(" -> ".join([str(p) for p in err.path]))
        else:
            err_path = ""
        errors.append(err.message + " " + err_path)
    return errors
