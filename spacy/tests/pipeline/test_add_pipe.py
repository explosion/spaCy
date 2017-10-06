from __future__ import unicode_literals
import pytest

from ... import language
from ...language import Language

@pytest.fixture
def nlp():
    return Language()

@pytest.fixture
def name():
    return 'parser'

def new_pipe(doc):
    return doc


def test_add_pipe_no_name(nlp):
    nlp.add_pipe(new_pipe)
    assert 'new_pipe' in nlp.pipe_names

def test_add_pipe_duplicate_name(nlp):
    nlp.add_pipe(new_pipe, name='duplicate_name')
    with pytest.raises(ValueError):
        nlp.add_pipe(new_pipe, name='duplicate_name')


def test_add_pipe_first(nlp, name):
    nlp.add_pipe(new_pipe, name=name, first=True)
    assert nlp.pipeline[0][0] == name


def test_add_pipe_last(nlp, name):
    nlp.add_pipe(lambda doc: doc, name='lambda_pipe')
    nlp.add_pipe(new_pipe, name=name, last=True)
    assert nlp.pipeline[0][0] != name
    assert nlp.pipeline[-1][0] == name


def test_cant_add_pipe_first_and_last(nlp):
    with pytest.raises(ValueError):
        nlp.add_pipe(new_pipe, first=True, last=True)
