from cymem.cymem cimport Pool
from thinc.backends.cblas cimport CBlas

from ..ml.parser_model cimport ActivationsC, SizesC, WeightsC
from ..vocab cimport Vocab
from ._parser_internals._state cimport StateC
from ._parser_internals.transition_system cimport Transition, TransitionSystem
from .trainable_pipe cimport TrainablePipe


cdef class Parser(TrainablePipe):
    cdef public object _rehearsal_model
    cdef readonly TransitionSystem moves
    cdef public object _multitasks

    cdef void _parseC(
        self,
        CBlas cblas,
        StateC** states,
        WeightsC weights,
        SizesC sizes
    ) nogil

    cdef void c_transition_batch(
        self,
        StateC** states,
        const float* scores,
        int nr_class,
        int batch_size
    ) nogil
