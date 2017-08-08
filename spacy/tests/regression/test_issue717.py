# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.models('en')
@pytest.mark.parametrize('text1,text2',
    [("You're happy", "You are happy"),
     ("I'm happy", "I am happy"),
     ("he's happy", "he's happy")])
def test_issue717(EN, text1, text2):
    """Test that contractions are assigned the correct lemma."""
    doc1 = EN(text1)
    doc2 = EN(text2)
    assert doc1[1].lemma_ == doc2[1].lemma_
    assert doc1[1].lemma == doc2[1].lemma
