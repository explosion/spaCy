# coding: utf-8
from __future__ import unicode_literals

from ..orth import is_alpha, is_digit, is_punct, is_space, is_ascii, is_upper
from ..orth import is_lower, is_title, like_url, like_number, word_shape

import pytest


# TODO: brackets, is_ascii, is_upper, is_lower, is_title


@pytest.mark.parametrize('text,match', [
    ('1997', False), ('19.97', False), ('hello9', False), ('Hello', True),
    ('HELLO', True), ('Hello9', False), ('\n', False), ('!', False),
    ('!d', False), ('\nd', False)])
def test_orth_is_alpha(text, match):
    if match:
        assert is_alpha(text)
    else:
        assert not is_alpha(text)


@pytest.mark.parametrize('text,match', [
    ('1997', True), ('0000000', True), ('19.97', False), ('hello9', False), ('Hello', False), ('\n', False), ('!', False), ('!0', False),
    ('\n5', False)])
def test_orth_is_digit(text, match):
    if match:
        assert is_digit(text)
    else:
        assert not is_digit(text)


@pytest.mark.parametrize('text,match', [(',', True), (' ', False), ('a', False)])
def test_orth_is_punct(text,match):
    if match:
        assert is_punct(text)
    else:
        assert not is_punct(text)


@pytest.mark.parametrize('text,match', [(',', False), (' ', True), ('a', False)])
def test_orth_is_space(text,match):
    if match:
        assert is_space(text)
    else:
        assert not is_space(text)


@pytest.mark.parametrize('text,match', [
    ('www.google.com', True), ('google.com', True), ('sydney.com', True),
    ('2girls1cup.org', True), ('http://stupid', True), ('www.hi', True),
    ('dog', False), ('1.2', False), ('1.a', False), ('hello.There', False)])
def test_orth_like_url(text, match):
    if match:
        assert like_url(text)
    else:
        assert not like_url(text)


@pytest.mark.parametrize('text,match', [
    ('10', True), ('1', True), ('10,000', True), ('10,00', True),
    (',10', True), ('999.0', True), ('one', True), ('two', True),
    ('billion', True), ('dog', False), (',', False), ('1/2', True),
    ('1/2/3', False)])
def test_orth_like_number(text, match):
    if match:
        assert like_number(text)
    else:
        assert not like_number(text)


@pytest.mark.parametrize('text,shape', [
    ('Nasa', 'Xxxx'), ('capitalized', 'xxxx'), ('999999999', 'dddd'),
    ('C3P0', 'XdXd'), (',', ','), ('\n', '\n'), ('``,-', '``,-')])
def test_orth_word_shape(text, shape):
    assert word_shape(text) == shape
