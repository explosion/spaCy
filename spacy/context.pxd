from thinc.typedefs cimport atom_t
from .typedefs cimport hash_t
from .tokens cimport Tokens
from .lexeme cimport Lexeme


cdef class Token:
    cdef readonly atom_t sic
    cdef readonly atom_t cluster
    cdef readonly atom_t norm
    cdef readonly atom_t shape
    cdef readonly atom_t asciied
    cdef readonly atom_t prefix
    cdef readonly atom_t suffix
    cdef readonly atom_t length

    cdef readonly atom_t postype
    cdef readonly atom_t nertype
    cdef readonly atom_t sensetype

    cdef readonly atom_t is_alpha
    cdef readonly atom_t is_ascii
    cdef readonly atom_t is_digit
    cdef readonly atom_t is_lower
    cdef readonly atom_t is_punct
    cdef readonly atom_t is_space
    cdef readonly atom_t is_title
    cdef readonly atom_t is_upper
    cdef readonly atom_t like_url
    cdef readonly atom_t like_number
    cdef readonly atom_t oft_lower
    cdef readonly atom_t oft_title
    cdef readonly atom_t oft_upper

    cdef readonly atom_t in_males
    cdef readonly atom_t in_females
    cdef readonly atom_t in_surnames
    cdef readonly atom_t in_places
    cdef readonly atom_t in_games
    cdef readonly atom_t in_celebs
    cdef readonly atom_t in_names

    cdef readonly atom_t pos
    cdef readonly atom_t sense
    cdef readonly atom_t ner


cdef class Slots:
    cdef readonly Token P4
    cdef readonly Token P3
    cdef readonly Token P2
    cdef readonly Token P1
    cdef readonly Token N0
    cdef readonly Token N1
    cdef readonly Token N2
    cdef readonly Token N3
    cdef readonly Token N4


cdef int N_FIELDS


cdef int fill_context(atom_t* context, int i, Tokens tokens) except -1


cpdef Slots FIELD_IDS
