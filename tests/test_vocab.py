from __future__ import unicode_literals

from spacy.en import EN


def test_neq():
    addr = EN.lookup('Hello')
    assert EN.lookup('bye') != addr


def test_eq():
    addr = EN.lookup('Hello')
    assert EN.lookup('Hello') == addr


def test_round_trip():
    hello = EN.lookup('Hello')
    assert hello.string == 'Hello'


def test_case_neq():
    addr = EN.lookup('Hello')
    assert EN.lookup('hello') != addr


def test_punct_neq():
    addr = EN.lookup('Hello')
    assert EN.lookup('Hello,') != addr


def test_short():
    addr = EN.lookup('I')
    assert addr.string == 'I'
    assert addr.string != 'not'
