from __future__ import unicode_literals

from spacy.en import EN


def test_neq():
    addr = EN.lexicon.lookup('Hello')
    assert EN.lexicon.lookup('bye').string != addr.string


def test_eq():
    addr = EN.lexicon.lookup('Hello')
    assert EN.lexicon.lookup('Hello').string == addr.string


def test_round_trip():
    hello = EN.lexicon.lookup('Hello')
    assert hello.string == 'Hello'


def test_case_neq():
    addr = EN.lexicon.lookup('Hello')
    assert EN.lexicon.lookup('hello').string != addr.string


def test_punct_neq():
    addr = EN.lexicon.lookup('Hello')
    assert EN.lexicon.lookup('Hello,').string != addr.string


def test_short():
    addr = EN.lexicon.lookup('I')
    assert addr.string == 'I'
    assert addr.string != 'not'
