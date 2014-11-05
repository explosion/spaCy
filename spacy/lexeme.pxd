from .typedefs cimport hash_t, utf8_t, flag_t, id_t, len_t, tag_t

from .utf8string cimport StringStore
from libc.stdint cimport uint16_t

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

    LIKE_URL
    LIKE_NUMBER

    OFT_LOWER
    OFT_TITLE
    OFT_UPPER

    IN_MALES
    IN_FEMALES
    IN_SURNAMES
    IN_PLACES
    IN_GAMES
    IN_CELEBS
    IN_NAMES


cdef struct Lexeme:
    flag_t flags
   
    id_t id
    id_t sic
    id_t norm
    id_t shape
    id_t asciied
    id_t prefix
    id_t suffix

    float prob
    
    len_t length
    tag_t cluster
    tag_t postype
    tag_t supersense


cdef Lexeme EMPTY_LEXEME

cpdef Lexeme init(id_t i, unicode string, hash_t hashed,
                  StringStore store, dict props) except *
 

cdef inline bint check_flag(Lexeme* lexeme, size_t flag_id) nogil:
    return lexeme.flags & (1 << flag_id)
