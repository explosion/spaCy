from ..vocab cimport Vocab


cdef class Packer:
    cdef readonly tuple attrs
    cdef readonly tuple _codecs
    cdef readonly object orth_codec
    cdef readonly object char_codec
    cdef readonly Vocab vocab
