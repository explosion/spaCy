from __future__ import unicode_literals

from spacy.ner.pystate import PyState
import pytest


@pytest.fixture
def labels():
    ent_types = ['LOC', 'MISC', 'ORG', 'PER']
    moves = ['B', 'I', 'L', 'U']
    labels = ['NULL', 'EOL', 'O']
    for move in moves:
        for ent_type in ent_types:
            labels.append('%s-%s' % (move, ent_type))
    return labels


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
    assert state.n_ents == 0
    assert state.i == 1
    assert state.open_entity
    assert state.ent == {'start': 0, 'label': 4, 'end': 0}
    assert state.is_valid('I-PER')
    assert not state.is_valid('I-LOC')
    assert state.is_valid('L-PER')
    assert not state.is_valid('L-LOC')
    assert not state.is_valid('O')
    assert not state.is_valid('U-PER')

def test_in(state, sentence):
    state.transition('B-PER')
    assert state.n_ents == 0
    state.transition('I-PER')
    assert state.n_ents == 0
    assert state.i == 2
    assert state.is_valid('I-PER')
    assert state.is_valid('L-PER')
    assert not state.is_valid('B-PER')
    assert not state.is_valid('I-LOC')
    assert not state.is_valid('L-LOC')
    assert not state.is_valid('U-PER')
    assert not state.is_valid('O')


def test_last(state, sentence):
    state.transition('B-PER')
    assert state.n_ents == 0
    state.transition('L-PER')
    assert state.n_ents == 1
    assert state.i == 2
    assert not state.open_entity
    assert state.is_valid('B-PER')
    assert state.is_valid('B-LOC')
    assert state.is_valid('U-PER')
    assert state.is_valid('U-LOC')
    assert state.is_valid('O')
    assert not state.is_valid('L-PER')
    assert not state.is_valid('I-PER')


def test_unit(state, sentence):
    assert state.n_ents == 0
    state.transition('U-PER')
    assert state.n_ents == 1
    assert state.i == 1
    assert not state.open_entity
    assert state.is_valid('B-PER')
    assert state.is_valid('B-LOC')
    assert state.is_valid('U-PER')
    assert state.is_valid('U-LOC')
    assert state.is_valid('O')
    assert not state.is_valid('I-PER')
    assert not state.is_valid('L-PER')


def test_out(state, sentence):
    assert state.n_ents == 0
    state.transition('U-PER')
    assert state.n_ents == 1
    assert state.i == 1
    state.transition('O')
    assert state.i == 2
    assert not state.open_entity
    assert state.is_valid('B-PER')
    assert state.is_valid('B-LOC')
    assert state.is_valid('U-PER')
    assert state.is_valid('U-LOC')
    assert state.is_valid('O')
    assert not state.is_valid('I-PER')
    assert not state.is_valid('L-PER')


@pytest.fixture
def golds(sentence):
    g = ['B-PER', 'L-PER', 'O', 'U-PER', 'O']
    assert len(g) == len(sentence)
    return g


def test_oracle_gold(state, sentence, golds):
    state.set_golds(golds)
    assert state.is_gold('B-PER')
    assert not state.is_gold('B-LOC')
    assert not state.is_gold('I-PER')
    assert not state.is_gold('L-PER')
    assert not state.is_gold('U-PER')
    assert not state.is_gold('O')
    state.transition('B-PER')
    assert state.is_gold('L-PER')
    state.transition('L-PER')
    assert state.is_gold('O')
    assert not state.is_gold('B-PER')
    state.transition('O')
    assert not state.is_gold('B-PER')
    assert not state.is_gold('O')
    assert state.is_gold('U-PER')
    state.transition('U-PER')
    assert state.is_gold('O')
    state.transition('O')
    assert state.i == len(sentence)


def test_oracle_miss_entity(state, sentence, golds):
    state.set_golds(golds)
    state.transition('O')
    assert not state.is_gold('L-PER')
    assert not state.is_gold('U-PER')
    assert not state.is_gold('I-PER')
    assert not state.is_gold('B-PER')
    assert state.is_gold('O')
    state.transition('O')
    state.transition('O')
    assert state.is_gold('U-PER')


def test_oracle_extend_entity(state, sentence, golds):
    state.set_golds(golds)
    state.transition('B-PER')
    assert not state.is_gold('I-PER')
    state.transition('I-PER')
    assert state.is_gold('L-PER')
    assert not state.is_gold('I-PER')
