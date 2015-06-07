from __future__ import unicode_literals

from spacy.orth import like_number


def test_digits():
    assert like_number('10')
    assert like_number('1')


def test_comma():
    assert like_number('10,000')
    assert like_number('10,00')
    assert like_number(',10')


def test_period():
    assert like_number('999.0')
    assert like_number('.99')


def test_fraction():
    assert like_number('1/2')
    assert not like_number('1/2/3')


def test_word():
    assert like_number('one')
    assert like_number('two')
    assert like_number('billion')


def test_not_number():
    assert not like_number('dog')
    assert not like_number(',')
