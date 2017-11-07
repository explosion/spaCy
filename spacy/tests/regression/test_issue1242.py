from __future__ import unicode_literals
import pytest
from ...lang.en import English
from ...util import load_model


def test_issue1242_empty_strings():
    nlp = English()
    doc = nlp('')
    assert len(doc) == 0
    docs = list(nlp.pipe(['', 'hello']))
    assert len(docs[0]) == 0
    assert len(docs[1]) == 1


@pytest.mark.models('en')
def test_issue1242_empty_strings_en_core_web_sm():
    nlp = load_model('en_core_web_sm')
    doc = nlp('')
    assert len(doc) == 0
    docs = list(nlp.pipe(['', 'hello']))
    assert len(docs[0]) == 0
    assert len(docs[1]) == 1
