# coding: utf8
from __future__ import unicode_literals


TOKEN_PATTERN_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema",
    "definitions": {
        "string_value": {
            "anyOf": [
                {"type": "string"},
                {
                    "type": "object",
                    "properties": {
                        "REGEX": {"type": "string"},
                        "IN": {"type": "array", "items": {"type": "string"}},
                        "NOT_IN": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
            ]
        },
        "integer_value": {
            "anyOf": [
                {"type": "integer"},
                {
                    "type": "object",
                    "properties": {
                        "REGEX": {"type": "string"},
                        "IN": {"type": "array", "items": {"type": "integer"}},
                        "NOT_IN": {"type": "array", "items": {"type": "integer"}},
                        "==": {"type": "integer"},
                        ">=": {"type": "integer"},
                        "<=": {"type": "integer"},
                        ">": {"type": "integer"},
                        "<": {"type": "integer"},
                    },
                    "additionalProperties": False,
                },
            ]
        },
        "boolean_value": {"type": "boolean"},
        "underscore_value": {
            "anyOf": [
                {"type": ["string", "integer", "number", "array", "boolean", "null"]},
                {
                    "type": "object",
                    "properties": {
                        "REGEX": {"type": "string"},
                        "IN": {
                            "type": "array",
                            "items": {"type": ["string", "integer"]},
                        },
                        "NOT_IN": {
                            "type": "array",
                            "items": {"type": ["string", "integer"]},
                        },
                        "==": {"type": "integer"},
                        ">=": {"type": "integer"},
                        "<=": {"type": "integer"},
                        ">": {"type": "integer"},
                        "<": {"type": "integer"},
                    },
                    "additionalProperties": False,
                },
            ]
        },
    },
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "ORTH": {
                "title": "Verbatim token text",
                "$ref": "#/definitions/string_value",
            },
            "TEXT": {
                "title": "Verbatim token text (spaCy v2.1+)",
                "$ref": "#/definitions/string_value",
            },
            "LOWER": {
                "title": "Lowercase form of token text",
                "$ref": "#/definitions/string_value",
            },
            "POS": {
                "title": "Coarse-grained part-of-speech tag",
                "$ref": "#/definitions/string_value",
            },
            "TAG": {
                "title": "Fine-grained part-of-speech tag",
                "$ref": "#/definitions/string_value",
            },
            "DEP": {"title": "Dependency label", "$ref": "#/definitions/string_value"},
            "LEMMA": {
                "title": "Lemma (base form)",
                "$ref": "#/definitions/string_value",
            },
            "SHAPE": {
                "title": "Abstract token shape",
                "$ref": "#/definitions/string_value",
            },
            "ENT_TYPE": {
                "title": "Entity label of single token",
                "$ref": "#/definitions/string_value",
            },
            "LENGTH": {
                "title": "Token character length",
                "$ref": "#/definitions/integer_value",
            },
            "IS_ALPHA": {
                "title": "Token consists of alphanumeric characters",
                "$ref": "#/definitions/boolean_value",
            },
            "IS_ASCII": {
                "title": "Token consists of ASCII characters",
                "$ref": "#/definitions/boolean_value",
            },
            "IS_DIGIT": {
                "title": "Token consists of digits",
                "$ref": "#/definitions/boolean_value",
            },
            "IS_LOWER": {
                "title": "Token is lowercase",
                "$ref": "#/definitions/boolean_value",
            },
            "IS_UPPER": {
                "title": "Token is uppercase",
                "$ref": "#/definitions/boolean_value",
            },
            "IS_TITLE": {
                "title": "Token  is titlecase",
                "$ref": "#/definitions/boolean_value",
            },
            "IS_PUNCT": {
                "title": "Token is punctuation",
                "$ref": "#/definitions/boolean_value",
            },
            "IS_SPACE": {
                "title": "Token is whitespace",
                "$ref": "#/definitions/boolean_value",
            },
            "IS_STOP": {
                "title": "Token is stop word",
                "$ref": "#/definitions/boolean_value",
            },
            "LIKE_NUM": {
                "title": "Token resembles a number",
                "$ref": "#/definitions/boolean_value",
            },
            "LIKE_URL": {
                "title": "Token resembles a URL",
                "$ref": "#/definitions/boolean_value",
            },
            "LIKE_EMAIL": {
                "title": "Token resembles an email address",
                "$ref": "#/definitions/boolean_value",
            },
            "_": {
                "title": "Custom extension token attributes (token._.)",
                "type": "object",
                "patternProperties": {
                    "^.*$": {"$ref": "#/definitions/underscore_value"}
                },
            },
            "OP": {
                "title": "Operators / quantifiers",
                "type": "string",
                "enum": ["+", "*", "?", "!"],
            },
        },
        "additionalProperties": False,
    },
}
