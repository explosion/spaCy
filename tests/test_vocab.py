from __future__ import unicode_literals

from spacy.en import EN


def test_neq():
    addr = EN.lookup('Hello')
    assert EN.lookup('bye').string != addr.string


def test_eq():
    addr = EN.lookup('Hello')
    assert EN.lookup('Hello').string == addr.string


def test_round_trip():
    hello = EN.lookup('Hello')
    assert hello.string == 'Hello'


def test_case_neq():
    addr = EN.lookup('Hello')
    assert EN.lookup('hello').string != addr.string


def test_punct_neq():
    addr = EN.lookup('Hello')
    assert EN.lookup('Hello,').string != addr.string


def test_short():
    addr = EN.lookup('I')
    assert addr.string == 'I'
    assert addr.string != 'not'
