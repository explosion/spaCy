from cymem.cymem cimport Pool

from ..vocab cimport Vocab
from .pipe cimport Pipe
from ._parser_internals.transition_system cimport Transition, TransitionSystem
from ._parser_internals._state cimport StateC
from ..ml.parser_model cimport WeightsC, ActivationsC, SizesC


cdef class Parser(Pipe):
    cdef readonly Vocab vocab
    cdef public object model
    cdef public object _rehearsal_model
    cdef readonly TransitionSystem moves
    cdef readonly object cfg
    cdef public object _multitasks

    cdef void _parseC(self, StateC** states,
            WeightsC weights, SizesC sizes) nogil

    cdef void c_transition_batch(self, StateC** states, const float* scores,
            int nr_class, int batch_size) nogil
