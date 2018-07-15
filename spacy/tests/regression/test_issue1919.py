'''Test that nlp.begin_training() doesn't require missing cfg properties.'''
from __future__ import unicode_literals
import pytest
from ... import load as load_spacy

@pytest.mark.models('en')
def test_issue1919():
    nlp = load_spacy('en')
    opt = nlp.begin_training()

