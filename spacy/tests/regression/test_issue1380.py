from __future__ import unicode_literals
import pytest

from ...language import Language

def test_issue1380_empty_string():
    nlp = Language()
    doc = nlp('')
    assert len(doc) == 0

@pytest.mark.models('en')
def test_issue1380_en(EN):
    doc = EN('')
    assert len(doc) == 0
