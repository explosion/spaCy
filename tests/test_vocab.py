from __future__ import unicode_literals

from spacy.en import EN


def test_neq():
    addr = EN.lexicon.lookup('Hello')
    assert EN.lexicon.lookup('bye')['id'] != addr['id']


def test_eq():
    addr = EN.lexicon.lookup('Hello')
    assert EN.lexicon.lookup('Hello')['id'] == addr['id']


def test_case_neq():
    addr = EN.lexicon.lookup('Hello')
    assert EN.lexicon.lookup('hello')['id'] != addr['id']


def test_punct_neq():
    addr = EN.lexicon.lookup('Hello')
    assert EN.lexicon.lookup('Hello,')['id'] != addr['id']
