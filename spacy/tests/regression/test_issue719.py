# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.models('en')
@pytest.mark.parametrize('text', ["s..."])
def test_issue719(EN, text):
    """Test that the token 's' is not lemmatized into empty string."""
    tokens = EN(text)
    assert tokens[0].lemma_ != ''
