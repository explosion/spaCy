from cymem.cymem cimport Pool

from ..structs cimport TokenC

cdef class GoldParse:
    cdef Pool mem

    cdef int* c_heads
    cdef int* c_labels

    cdef int length
    cdef int loss

    cdef unicode raw_text
    cdef list words
    cdef list ids
    cdef list tags
    cdef list heads
    cdef list labels


    cdef int heads_correct(self, TokenC* tokens, bint score_punct=?) except -1
