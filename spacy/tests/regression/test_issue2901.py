import pytest
import spacy


def test_issue2901():
    '''Test that `nlp` doesn't fail.'''
    try:
        nlp = spacy.blank('ja')
    except ImportError:
        pytest.skip()

    doc = nlp('pythonが大好きです')
    assert doc
