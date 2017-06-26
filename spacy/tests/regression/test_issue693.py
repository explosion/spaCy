# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.xfail
@pytest.mark.models('en')
def test_issue693(EN):
    """Test that doc.noun_chunks parses the complete sentence."""

    text1 = "the TopTown International Airport Board and the Goodwill Space Exploration Partnership."
    text2 = "the Goodwill Space Exploration Partnership and the TopTown International Airport Board."
    doc1 = EN(text1)
    doc2 = EN(text2)
    chunks1 = [chunk for chunk in doc1.noun_chunks]
    chunks2 = [chunk for chunk in doc2.noun_chunks]
    assert len(chunks1) == 2
    assert len(chunks2) == 2
