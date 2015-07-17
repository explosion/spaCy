from ..vocab cimport Vocab


cdef class Packer:
    cdef readonly tuple attrs
    cdef readonly tuple _codecs
    cdef readonly Vocab vocab
