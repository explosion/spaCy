from .typedefs cimport hash_t, utf8_t, flag_t, id_t

from thinc.typedefs cimport atom_t

from .utf8string cimport StringStore

cpdef flag_t OOV_DIST_FLAGS

# Flags
cpdef enum:
    IS_ALPHA
    IS_ASCII
    IS_DIGIT
    IS_LOWER
    IS_PUNCT
    IS_SPACE
    IS_TITLE
    IS_UPPER

    OFT_LOWER
    OFT_TITLE
    OFT_UPPER


cdef struct Lexeme:
    atom_t length
   
    atom_t sic
    atom_t norm
    atom_t shape
    atom_t vocab10k
    atom_t asciied
    atom_t prefix
    atom_t suffix

    atom_t cluster
    atom_t pos
    atom_t supersense

    float prob

    flag_t flags


cdef Lexeme EMPTY_LEXEME

cpdef Lexeme init(unicode string, hash_t hashed,
                  StringStore store, dict props) except *
 

cdef inline bint check_flag(Lexeme* lexeme, size_t flag_id) nogil:
    return lexeme.flags & (1 << flag_id)
