from __future__ import unicode_literals

from spacy.ner.pystate import PyState
import pytest


@pytest.fixture
def labels():
    return ['LOC', 'MISC', 'ORG', 'PER']


def test_n_moves(labels):
    s = PyState(labels, 5)
    b_moves = len(labels)
    i_moves = len(labels)
    l_moves = len(labels)
    u_moves = len(labels)
    o_moves = 1
    assert s.n_classes == b_moves + i_moves + l_moves + u_moves + o_moves

@pytest.fixture
def sentence():
    return "Ms. Haag plays Elianti .".split()


@pytest.fixture
def state(labels, sentence):
    return PyState(labels, len(sentence))


def test_begin(state, sentence):
    assert state.n_ents == 0
    assert state.i == 0
    state.transition('B-PER')
    assert state.n_ents == 1
    assert state.i == 1
    assert state.open_entity
    assert state.ent == {'start': 0, 'label': 3, 'end': 0}
