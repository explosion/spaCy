import pytest

from spacy.pipeline._parser_internals.stateclass import StateClass
from spacy.tokens.doc import Doc
from spacy.vocab import Vocab


@pytest.fixture
def vocab():
    return Vocab()


@pytest.fixture
def doc(vocab):
    return Doc(vocab, words=["a", "b", "c", "d"])


def test_init_state(doc):
    state = StateClass(doc)
    assert state.stack == []
    assert state.queue == list(range(len(doc)))
    assert not state.is_final()
    assert state.buffer_length() == 4


def test_push_pop(doc):
    state = StateClass(doc)
    state.push()
    assert state.buffer_length() == 3
    assert state.stack == [0]
    assert 0 not in state.queue
    state.push()
    assert state.stack == [1, 0]
    assert 1 not in state.queue
    assert state.buffer_length() == 2
    state.pop()
    assert state.stack == [0]
    assert 1 not in state.queue


def test_stack_depth(doc):
    state = StateClass(doc)
    assert state.stack_depth() == 0
    assert state.buffer_length() == len(doc)
    state.push()
    assert state.buffer_length() == 3
    assert state.stack_depth() == 1


def test_H(doc):
    state = StateClass(doc)
    assert state.H(0) == -1
    state.add_arc(1, 0, 0)
    assert state.arcs == [{"head": 1, "child": 0, "label": 0}]
    assert state.H(0) == 1
    state.add_arc(3, 1, 0)
    assert state.H(1) == 3


def test_L(doc):
    state = StateClass(doc)
    assert state.L(2, 1) == -1
    state.add_arc(2, 1, 0)
    assert state.arcs == [{"head": 2, "child": 1, "label": 0}]
    assert state.L(2, 1) == 1
    state.add_arc(2, 0, 0)
    assert state.L(2, 1) == 0
    assert state.n_L(2) == 2


def test_R(doc):
    state = StateClass(doc)
    assert state.R(0, 1) == -1
    state.add_arc(0, 1, 0)
    assert state.arcs == [{"head": 0, "child": 1, "label": 0}]
    assert state.R(0, 1) == 1
    state.add_arc(0, 2, 0)
    assert state.R(0, 1) == 2
    assert state.n_R(0) == 2
