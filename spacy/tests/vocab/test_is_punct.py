from __future__ import unicode_literals


from spacy.orth import is_punct


def test_comma():
    assert is_punct(',')


def test_space():
    assert not is_punct(' ')


def test_letter():
    assert not is_punct('a')
