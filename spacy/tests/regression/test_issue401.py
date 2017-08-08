# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.models('en')
@pytest.mark.parametrize('text,i', [("Jane's got a new car", 1),
                                    ("Jane thinks that's a nice car", 3)])
def test_issue401(EN, text, i):
    """Text that 's in contractions is not lemmatized as '."""
    tokens = EN(text)
    assert tokens[i].lemma_ != "'"
