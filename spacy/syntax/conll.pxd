from ..structs cimport TokenC


cdef class GoldParse:
    cdef int* heads
    cdef int* labels
    cdef int heads_correct(self, TokenC* tokens, bint score_punct=?) except -1
