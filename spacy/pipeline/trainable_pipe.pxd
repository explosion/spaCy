from .pipe cimport Pipe

cdef class TrainablePipe(Pipe):
    cdef public object model
