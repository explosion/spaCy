from ..vocab cimport Vocab


cdef class Packer:
    cdef tuple _codecs
    cdef Vocab vocab
