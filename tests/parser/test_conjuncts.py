"""Test the Token.conjuncts property"""
from __future__ import unicode_literals

from spacy.en import English
import pytest


def orths(tokens):
    return [t.orth_ for t in tokens]


def test_simple_two():
    nlp = English()
    tokens = nlp('I lost money and pride.', tag=True, parse=True)
    pride = tokens[4]
    for t in tokens:
        print t.orth_, t.tag_, t.head.orth_
    assert orths(pride.conjuncts) == ['money', 'pride']
    money = tokens[2]
    assert orths(money.conjuncts) == ['money', 'pride']


def test_comma_three():
    nlp = English()
    tokens = nlp('I found my wallet, phone and keys.')
    keys = tokens[-2]
    assert orths(keys.conjuncts) == ['wallet', 'phone', 'keys']
    wallet = tokens[3]
    assert orths(wallet.conjuncts) == ['wallet', 'phone', 'keys']


# This is failing due to parse errors
#def test_and_three():
#    tokens = NLU('I found my wallet and phone and keys.')
#    keys = tokens[-2]
#    assert orths(keys.conjuncts) == ['wallet', 'phone', 'keys']
#    wallet = tokens[3]
#    assert orths(wallet.conjuncts) == ['wallet', 'phone', 'keys']
