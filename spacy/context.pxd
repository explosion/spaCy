from thinc.typedefs cimport atom_t
from .typedefs cimport hash_t
from .tokens cimport Tokens
from .lexeme cimport Lexeme


cdef class Token:
    cdef readonly atom_t i
    cdef readonly atom_t c
    cdef readonly atom_t w
    cdef readonly atom_t shape
    cdef readonly atom_t pref
    cdef readonly atom_t suff
    cdef readonly atom_t oft_title
    cdef readonly atom_t oft_upper
    cdef readonly atom_t is_alpha
    cdef readonly atom_t is_digit
    cdef readonly atom_t is_title
    cdef readonly atom_t is_upper

    cdef readonly atom_t url
    cdef readonly atom_t num

    cdef readonly atom_t postype
    cdef readonly atom_t pos
    cdef readonly atom_t ner


cdef class Slots:
    cdef readonly Token P2
    cdef readonly Token P1
    cdef readonly Token N0
    cdef readonly Token N1
    cdef readonly Token N2


cdef int N_FIELDS


cdef hash_t fill_slots(Slots s, int i, Tokens tokens) except 0

cdef int fill_flat(atom_t* context, Slots s) except -1


cpdef Slots FIELD_IDS
