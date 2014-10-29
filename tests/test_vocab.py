from __future__ import unicode_literals

from spacy.en import EN


def test_neq():
    addr = EN.lexicon.lookup('Hello')
    assert EN.lexicon.lookup('bye')['sic'] != addr['sic']


def test_eq():
    addr = EN.lexicon.lookup('Hello')
    assert EN.lexicon.lookup('Hello')['sic'] == addr['sic']


def test_case_neq():
    addr = EN.lexicon.lookup('Hello')
    assert EN.lexicon.lookup('hello')['sic'] != addr['sic']


def test_punct_neq():
    addr = EN.lexicon.lookup('Hello')
    assert EN.lexicon.lookup('Hello,')['sic'] != addr['sic']
