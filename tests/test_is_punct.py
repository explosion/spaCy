from __future__ import unicode_literals


from spacy.orth import is_punct


def test_comma():
    assert is_punct(',', 0, {}, {}) == True


def test_space():
    assert is_punct(' ', 0, {}, {}) == False


def test_letter():
    assert is_punct('a', 0, {}, {}) == False
