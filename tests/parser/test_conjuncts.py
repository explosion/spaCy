"""Test the Token.conjuncts property"""
from __future__ import unicode_literals

import pytest


def orths(tokens):
    return [t.orth_ for t in tokens]


#def test_simple_two(EN):
#    tokens = EN('I lost money and pride.', tag=True, parse=True)
#    pride = tokens[4]
#    assert orths(pride.conjuncts) == ['money', 'pride']
#    money = tokens[2]
#    assert orths(money.conjuncts) == ['money', 'pride']


#def test_comma_three(EN):
#    tokens = EN('I found my wallet, phone and keys.')
#    keys = tokens[-2]
#    assert orths(keys.conjuncts) == ['wallet', 'phone', 'keys']
#    wallet = tokens[3]
#    assert orths(wallet.conjuncts) == ['wallet', 'phone', 'keys']


# This is failing due to parse errors
#def test_and_three():
#    tokens = NLU('I found my wallet and phone and keys.')
#    keys = tokens[-2]
#    assert orths(keys.conjuncts) == ['wallet', 'phone', 'keys']
#    wallet = tokens[3]
#    assert orths(wallet.conjuncts) == ['wallet', 'phone', 'keys']
