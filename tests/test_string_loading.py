"""Test suspected freeing of strings"""
from __future__ import unicode_literals

import pytest

from spacy.en import EN


def test_one():
    tokens = EN.tokenize('Betty Botter bought a pound of butter.')
    assert tokens[0].string == 'Betty'
    tokens2 = EN.tokenize('Betty also bought a pound of butter.')
    assert tokens2[0].string == 'Betty'



