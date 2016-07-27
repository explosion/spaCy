"""Test suspected freeing of strings"""
from __future__ import unicode_literals


def test_one(en_tokenizer):
    tokens = en_tokenizer('Betty Botter bought a pound of butter.')
    assert tokens[0].orth_ == 'Betty'
    tokens2 = en_tokenizer('Betty also bought a pound of butter.')
    assert tokens2[0].orth_ == 'Betty'
