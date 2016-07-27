from ..vocab cimport Vocab
from ..structs cimport TokenC
from ..attrs cimport attr_id_t
from .doc cimport Doc


cdef class Token:
    cdef Vocab vocab
    cdef TokenC* c
    cdef readonly int i
    cdef int array_len
    cdef readonly Doc doc

    @staticmethod
    cdef inline Token cinit(Vocab vocab, const TokenC* token, int offset, Doc doc):
        if offset < 0 or offset >= doc.length:
            msg = "Attempt to access token at %d, max length %d"
            raise IndexError(msg % (offset, doc.length))
        if doc._py_tokens[offset] != None:
            return doc._py_tokens[offset]
        cdef Token self = Token.__new__(Token, vocab, doc, offset)
        doc._py_tokens[offset] = self
        return self

    cpdef bint check_flag(self, attr_id_t flag_id) except -1
