from __future__ import unicode_literals

from spacy import lex_of
from spacy.en import lookup
from spacy.en import unhash


def test_neq():
    addr = lookup('Hello')
    assert lookup('bye') != addr


def test_eq():
    addr = lookup('Hello')
    assert lookup('Hello') == addr


def test_round_trip():
    hello = lookup('Hello')
    assert unhash(hello.lex) == 'Hello'


def test_case_neq():
    addr = lookup('Hello')
    assert lookup('hello') != addr


def test_punct_neq():
    addr = lookup('Hello')
    assert lookup('Hello,') != addr


def test_short():
    addr = lookup('I')
    assert unhash(addr.lex) == 'I'
    addr = lookup('not')
    assert unhash(addr.lex) == 'not'
