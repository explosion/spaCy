from __future__ import unicode_literals
from itertools import chain

import numpy as np

from ..tokens import Doc, Span, Token
from ..sklearn import *

import pytest


texts = [
    'Hello, World!',
    '',
    'This is a test for SpaCy Scikit-learn wrapper created by Pager.',
    'Pager is an American health care startup. It was founded in 2015.'
    ]

# list out all properties of a Token and their types
bool_properties = [
    'is_alpha', 'is_ascii', 'is_digit', 'is_lower', 'is_title', 'is_punct',
    'is_space', 'is_oov', 'is_stop', 'like_url', 'like_num', 'like_email'
]
float_properties = ['prob', 'sentiment']
int_properties = [
    'ent_type', 'ent_iob', 'ent_id', 'lemma', 'orth', 'lower', 'shape',
    'prefix', 'suffix', 'pos', 'tag', 'dep', 'lang'
]
str_properties = [p + '_' for p in int_properties]
int_properties.extend(['i', 'idx', 'lex_id'])
str_properties.extend(['text', 'text_with_ws', 'whitespace_'])


@pytest.mark.models
def test_sklearn_constructor(EN):
    transformer = SpacyTransformer(model=EN)
    assert transformer.model is EN
    assert hasattr(Token, transformer.token_property)


@pytest.mark.models
def test_transform_doc(EN):
    transformer = SpacyTransformer(model=EN, output_feature=DOC)
    processed_texts = transformer.transform(texts)
    assert len(texts) == len(processed_texts)
    for text in processed_texts:
        assert isinstance(text, Doc)


@pytest.mark.models
@pytest.mark.parametrize("output", [SENTENCES, ENTITIES, NOUN_CHUNKS])
def test_sklearn_transform_spans(EN, output):
    transformer = SpacyTransformer(model=EN, output_feature=output)
    spans = transformer.transform(texts)
    assert len(texts) == len(spans)
    for text in chain.from_iterable(spans):
        assert isinstance(text, Span)


@pytest.mark.models
def test_sklearn_transform_vector(EN):
    transformer = SpacyTransformer(model=EN, output_feature=VECTOR)
    vectors = transformer.transform(texts)
    assert isinstance(vectors, np.ndarray)
    assert len(texts) == vectors.shape[0]


@pytest.mark.models
@pytest.mark.parametrize("token_properties,expected_type", [
    (bool_properties, bool),
    (float_properties, float),
    (int_properties, int),
    (str_properties, str)
])
def test_sklearn_transform_tokens(EN, token_properties, expected_type):
    # test the property transformations exhaustively
    transformer = SpacyTransformer(model=EN, output_feature=TOKENS)
    for token_property in token_properties:
        transformer.token_property = token_property
        tokens = transformer.transform(texts)
        assert len(texts) == len(tokens)
        for token in chain.from_iterable(tokens):
            assert isinstance(token, expected_type)
