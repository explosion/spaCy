# cython: infer_types=True, binding=True
from cymem.cymem cimport Pool

from spacy.pipeline._parser_internals.search cimport Beam, MaxViolation
from spacy.typedefs cimport class_t

import pytest

from ..conftest import cytest


cdef struct TestState:
    int length
    int x
    char *string


cdef int transition(void* dest, void* src, class_t clas, void* extra_args) except -1:
    dest_state = <TestState*>dest
    src_state = <TestState*>src
    dest_state.length = src_state.length
    dest_state.x = src_state.x
    dest_state.x += clas
    if extra_args != NULL:
        dest_state.string = <char *>extra_args
    else:
        dest_state.string = src_state.string


cdef void* initialize(Pool mem, int n, void* extra_args) except NULL:
    state = <TestState*>mem.alloc(1, sizeof(TestState))
    state.length = n
    state.x = 1
    if extra_args == NULL:
        state.string = 'default'
    else:
        state.string = <char *>extra_args
    return state


cdef int destroy(Pool mem, void* state, void* extra_args) except -1:
    state = <TestState*>state
    mem.free(state)


@cytest
@pytest.mark.parametrize("nr_class,beam_width",
                         [
                             (2, 3),
                             (3, 6),
                             (4, 20),
                         ]
                         )
def test_init(nr_class, beam_width):
    b = Beam(nr_class, beam_width)
    assert b.size == 1
    assert b.width == beam_width
    assert b.nr_class == nr_class


@cytest
def test_init_violn():
    MaxViolation()


@cytest
@pytest.mark.parametrize("nr_class,beam_width,length",
                         [
                             (2, 3, 3),
                             (3, 6, 15),
                             (4, 20, 32),
                         ]
                         )
def test_initialize(nr_class, beam_width, length):
    b = Beam(nr_class, beam_width)
    b.initialize(initialize, destroy, length, NULL)
    for i in range(b.width):
        s = <TestState*>b.at(i)
        assert s.length == length, s.length
        assert s.string.decode('utf8') == 'default'


@cytest
@pytest.mark.parametrize("nr_class,beam_width,length,extra",
                         [
                             (2, 3, 4, None),
                             (3, 6, 15, u"test beam 1"),
                         ]
                         )
def test_initialize_extra(nr_class, beam_width, length, extra):
    extra = extra.encode("utf-8") if extra is not None else None
    b = Beam(nr_class, beam_width)
    if extra is None:
        b.initialize(initialize, destroy, length, NULL)
    else:
        b.initialize(initialize, destroy, length, <void*><char*>extra)
    for i in range(b.width):
        s = <TestState*>b.at(i)
        assert s.length == length


@cytest
@pytest.mark.parametrize("nr_class,beam_width,length",
                         [
                             (3, 6, 15),
                             (4, 20, 32),
                         ]
                         )
def test_transition(nr_class, beam_width, length):
    b = Beam(nr_class, beam_width)
    b.initialize(initialize, destroy, length, NULL)
    b.set_cell(0, 2, 30, True, 0)
    b.set_cell(0, 1, 42, False, 0)
    b.advance(transition, NULL, NULL)
    assert b.size == 1, b.size
    assert b.score == 30, b.score
    s = <TestState*>b.at(0)
    assert s.x == 3
    assert b._states[0].score == 30, b._states[0].score
    b.set_cell(0, 1, 10, True, 0)
    b.set_cell(0, 2, 20, True, 0)
    b.advance(transition, NULL, NULL)
    assert b._states[0].score == 50, b._states[0].score
    assert b._states[1].score == 40
    s = <TestState*>b.at(0)
    assert s.x == 5
