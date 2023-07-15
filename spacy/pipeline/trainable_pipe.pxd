from ..vocab cimport Vocab
from .pipe cimport Pipe


cdef class TrainablePipe(Pipe):
    cdef public Vocab vocab
    cdef public object model
    cdef public object cfg
    cdef public object scorer
