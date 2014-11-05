from thinc.typedefs cimport atom_t
from .typedefs cimport hash_t
from .tokens cimport Tokens
from .lexeme cimport Lexeme


cdef struct Token:
    atom_t i
    atom_t c
    atom_t w
    atom_t shape
    atom_t pref
    atom_t suff
    atom_t oft_title
    atom_t oft_upper
    atom_t is_alpha
    atom_t is_digit
    atom_t is_title
    atom_t is_upper

    atom_t url
    atom_t num

    atom_t postype
    atom_t pos
    atom_t ner


cdef struct Slots:
    Token P2
    Token P1
    Token N0
    Token N1
    Token N2


cdef Slots FIELD_IDS
cdef int N_FIELDS


cdef hash_t fill_slots(Slots* s, int i, Tokens tokens) except 0

cdef int fill_flat(atom_t* context, Slots* s) except -1
