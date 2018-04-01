import pytest

from ...tokens.doc import Doc
from ...vocab import Vocab
from ...syntax.stateclass import StateClass


def get_doc(words, vocab=None):
    if vocab is None:
        vocab = Vocab()
    return Doc(vocab, words=list(words))

def test_push():
    '''state.push_stack() should take the first word in the queue (aka buffer)
    and put it on the stack, popping that word from the queue.'''
    doc = get_doc('abcd')
    state = StateClass(doc)
    assert state.get_B(0) == 0
    state.push_stack()
    assert state.get_B(0) == 1

def test_pop():
    '''state.pop_stack() should remove the top word from the stack.'''
    doc = get_doc('abcd')
    state = StateClass(doc)
    assert state.get_B(0) == 0
    state.push_stack()
    state.push_stack()
    assert state.get_S(0) == 1
    assert state.get_S(1) == 0
    state.pop_stack()
    assert state.get_S(0) == 0

def test_unshift():
    doc = get_doc('abcd')
    state = StateClass(doc)
    state.push_stack()
    state.push_stack()
    state.unshift()
    assert state.get_B(0) == 1
    assert state.get_S(0) == 0
 
def test_break():
    doc = get_doc('abcd')
    state = StateClass(doc)
    state.push_stack()
    state.push_stack()
    assert state.get_B(0) == 2
    state.set_break(0)
    assert state.get_B(0) == -1
    state.unshift()
    assert state.get_B(0) == 1
    assert state.get_S(0) == 0
    state.push_stack()
    assert state.get_B(0) == -1
    assert state.get_S(0) == 1
    state.push_stack()
    assert state.get_B(0) == 3
    assert state.get_S(0) == 2
 
def test_cant_push_empty_buffer(): 
    doc = get_doc('a')
    state = StateClass(doc)
    state.push_stack()
    assert not state.can_push()

def test_cant_pop_empty_stack(): 
    doc = get_doc('a')
    state = StateClass(doc)
    assert not state.can_pop()
    state.push_stack()
    assert state.can_pop()
    state.pop_stack()
    assert not state.can_pop()
 
def test_can_pop_empty_buffer(): 
    doc = get_doc('ab')
    state = StateClass(doc)
    state.push_stack()
    state.push_stack()
    assert state.can_pop()
 
def test_cant_arc_empty_buffer(): 
    doc = get_doc('ab')
    state = StateClass(doc)
    state.push_stack()
    state.push_stack()
    assert not state.can_arc()
  
def test_cant_arc_empty_stack(): 
    doc = get_doc('ab')
    state = StateClass(doc)
    assert not state.can_arc()
    state.push_stack()
    assert state.can_arc()
    state.push_stack()
    state.pop_stack()
    state.pop_stack()
    assert not state.can_arc()

def test_cant_break_empty_buffer():
    doc = get_doc('ab')
    state = StateClass(doc)
    state.push_stack()
    state.push_stack()
    assert not state.can_break()
 
