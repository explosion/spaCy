from ..vocab cimport Vocab
from ..structs cimport TokenC
from ..typedefs cimport attr_id_t


cdef class Token:
    cdef Vocab vocab
    cdef const TokenC* c
    cdef readonly int i
    cdef int array_len
    cdef bint _owns_c_data
    cdef list _py_tokens

    @staticmethod
    cdef inline Token cinit(Vocab vocab, const TokenC* token, int offset, int array_len,
                            list _py_tokens):
        if offset < 0 or offset >= array_len:
            msg = "Attempt to access token at %d, max length %d"
            raise IndexError(msg % (offset, array_len))
        if _py_tokens[offset] != None:
            return _py_tokens[offset]
        cdef Token self = Token.__new__(Token, vocab)
        self.c = token
        self.i = offset
        self.array_len = array_len
        self._py_tokens = _py_tokens
        self._py_tokens[offset] = self
        return self

    cdef int take_ownership_of_c_data(self) except -1

    cpdef bint check_flag(self, attr_id_t flag_id) except -1
