from ._ml cimport Model
from thinc.nn cimport InputLayer


cdef class TheanoModel(Model):
    cdef InputLayer input_layer
    cdef object train_func
    cdef object predict_func
    cdef object debug

    cdef public float eta
    cdef public float mu
    cdef public float t
