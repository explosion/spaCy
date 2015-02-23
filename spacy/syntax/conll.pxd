from cymem.cymem cimport Pool

from ..structs cimport TokenC

cdef class GoldParse:
    cdef Pool mem

    cdef int* c_heads
    cdef int* c_labels

    cdef int length
    cdef int loss

    cdef readonly unicode raw_text
    cdef readonly list words
    cdef readonly list ids
    cdef readonly list tags
    cdef readonly list heads
    cdef readonly list labels


    cdef int heads_correct(self, TokenC* tokens, bint score_punct=?) except -1
