# coding: utf-8
from __future__ import unicode_literals


# NB: This schema describes the new format of the training data, see #2928
TRAINING_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema",
    "title": "Training data for spaCy models",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "text": {
                "title": "The text of the training example",
                "type": "string",
                "minLength": 1,
            },
            "ents": {
                "title": "Named entity spans in the text",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "title": "Start character offset of the span",
                            "type": "integer",
                            "minimum": 0,
                        },
                        "end": {
                            "title": "End character offset of the span",
                            "type": "integer",
                            "minimum": 0,
                        },
                        "label": {
                            "title": "Entity label",
                            "type": "string",
                            "minLength": 1,
                            "pattern": "^[A-Z0-9]*$",
                        },
                    },
                    "required": ["start", "end", "label"],
                },
            },
            "sents": {
                "title": "Sentence spans in the text",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "title": "Start character offset of the span",
                            "type": "integer",
                            "minimum": 0,
                        },
                        "end": {
                            "title": "End character offset of the span",
                            "type": "integer",
                            "minimum": 0,
                        },
                    },
                    "required": ["start", "end"],
                },
            },
            "cats": {
                "title": "Text categories for the text classifier",
                "type": "object",
                "patternProperties": {
                    "*": {
                        "title": "A text category",
                        "oneOf": [
                            {"type": "boolean"},
                            {"type": "number", "minimum": 0},
                        ],
                    }
                },
                "propertyNames": {"pattern": "^[A-Z0-9]*$", "minLength": 1},
            },
            "tokens": {
                "title": "The tokens in the text",
                "type": "array",
                "items": {
                    "type": "object",
                    "minProperties": 1,
                    "properties": {
                        "id": {
                            "title": "Token ID, usually token index",
                            "type": "integer",
                            "minimum": 0,
                        },
                        "start": {
                            "title": "Start character offset of the token",
                            "type": "integer",
                            "minimum": 0,
                        },
                        "end": {
                            "title": "End character offset of the token",
                            "type": "integer",
                            "minimum": 0,
                        },
                        "pos": {
                            "title": "Coarse-grained part-of-speech tag",
                            "type": "string",
                            "minLength": 1,
                        },
                        "tag": {
                            "title": "Fine-grained part-of-speech tag",
                            "type": "string",
                            "minLength": 1,
                        },
                        "dep": {
                            "title": "Dependency label",
                            "type": "string",
                            "minLength": 1,
                        },
                        "head": {
                            "title": "Index of the token's head",
                            "type": "integer",
                            "minimum": 0,
                        },
                    },
                    "required": ["start", "end"],
                },
            },
            "_": {"title": "Custom user space", "type": "object"},
        },
        "required": ["text"],
    },
}

META_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema",
    "type": "object",
    "properties": {
        "lang": {
            "title": "Two-letter language code, e.g. 'en'",
            "type": "string",
            "minLength": 2,
            "maxLength": 2,
            "pattern": "^[a-z]*$",
        },
        "name": {
            "title": "Model name",
            "type": "string",
            "minLength": 1,
            "pattern": "^[a-z_]*$",
        },
        "version": {
            "title": "Model version",
            "type": "string",
            "minLength": 1,
            "pattern": "^[0-9a-z.-]*$",
        },
        "spacy_version": {
            "title": "Compatible spaCy version identifier",
            "type": "string",
            "minLength": 1,
            "pattern": "^[0-9a-z.-><=]*$",
        },
        "parent_package": {
            "title": "Name of parent spaCy package, e.g. spacy or spacy-nightly",
            "type": "string",
            "minLength": 1,
            "default": "spacy",
        },
        "pipeline": {
            "title": "Names of pipeline components",
            "type": "array",
            "items": {"type": "string", "minLength": 1},
        },
        "description": {"title": "Model description", "type": "string"},
        "license": {"title": "Model license", "type": "string"},
        "author": {"title": "Model author name", "type": "string"},
        "email": {"title": "Model author email", "type": "string", "format": "email"},
        "url": {"title": "Model author URL", "type": "string", "format": "uri"},
        "sources": {
            "title": "Training data sources",
            "type": "array",
            "items": {"type": "string"},
        },
        "vectors": {
            "title": "Included word vectors",
            "type": "object",
            "properties": {
                "keys": {
                    "title": "Number of unique keys",
                    "type": "integer",
                    "minimum": 0,
                },
                "vectors": {
                    "title": "Number of unique vectors",
                    "type": "integer",
                    "minimum": 0,
                },
                "width": {
                    "title": "Number of dimensions",
                    "type": "integer",
                    "minimum": 0,
                },
            },
        },
        "accuracy": {
            "title": "Accuracy numbers",
            "type": "object",
            "patternProperties": {"*": {"type": "number", "minimum": 0.0}},
        },
        "speed": {
            "title": "Speed evaluation numbers",
            "type": "object",
            "patternProperties": {
                "*": {
                    "oneOf": [
                        {"type": "number", "minimum": 0.0},
                        {"type": "integer", "minimum": 0},
                    ]
                }
            },
        },
    },
    "required": ["lang", "name", "version"],
}
