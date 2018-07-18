from __future__ import unicode_literals
import pytest

from ...language import Language

def test_issue1380_empty_string():
    nlp = Language()
    doc = nlp('')
    assert len(doc) == 0
