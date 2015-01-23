"""Test suspected freeing of strings"""
from __future__ import unicode_literals

import pytest

from spacy.en import English


@pytest.fixture
def EN():
    return English()


def test_one(EN):
    tokens = EN('Betty Botter bought a pound of butter.')
    assert tokens[0].orth_ == 'Betty'
    tokens2 = EN('Betty also bought a pound of butter.')
    assert tokens2[0].orth_ == 'Betty'



