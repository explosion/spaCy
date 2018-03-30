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


def toy_split():
    def _realloc(data, new_size):
        additions = new_size - len(data)
        return data + ['']*additions
    length = 10
    sent = list(range(length))
    sent = [None]*pad + sent + [None]*pad # pad
    ptr = pad
    i = 5
    n = 2

    ptr -= pad
    i += pad
    sent = _realloc(sent, length+n+(pad*2))
    n_moved = (length + (pad*2)) - i+1



def test_split():
    '''state.split_token should take the ith word of the buffer, and split it
    into n+1 pieces. n is 0-indexed, i.e. split(i, 0) is a noop, and split(i, 1)
    creates 1 new token.'''
    doc = get_doc('abcd')
    state = StateClass(doc)
    assert len(state) == len(doc)
    state.split_token(1, 2)
    assert len(state) == len(doc)+2
    stdoc = state.get_doc(doc.vocab)
    assert stdoc[0].text == 'a'
    assert stdoc[1].text == 'b'
    assert stdoc[2].text == 'b'
    assert stdoc[3].text == 'b'
    assert stdoc[4].text == 'c'
    assert stdoc[5].text == 'd'
