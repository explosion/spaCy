"""Test suspected freeing of strings"""
from __future__ import unicode_literals

import pytest

from spacy.en import EN


def test_one():
    tokens = EN.tokenize('Betty Botter bought a pound of butter.')
    assert tokens.string(0) == 'Betty'
    tokens2 = EN.tokenize('Betty also bought a pound of butter.')
    assert tokens2.string(0) == 'Betty'



