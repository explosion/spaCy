from thinc.typedefs cimport atom_t

from .stateclass cimport StateClass
from .arc_eager cimport TransitionSystem
from ..vocab cimport Vocab
from ..tokens.doc cimport Doc
from ..structs cimport TokenC
from ._state cimport StateC
from ._parser_model cimport WeightsC, ActivationsC, SizesC


cdef class Parser:
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
