from ..vocab cimport Vocab


cdef class Packer:
    cdef readonly tuple attrs
    cdef readonly tuple _codecs
    cdef readonly object lex_codec
    cdef readonly Vocab vocab
