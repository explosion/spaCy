cdef enum OrthFlag:
    IS_ALPHA
    IS_DIGIT
    IS_PUNCT
    IS_SPACE
    IS_LOWER
    IS_UPPER
    IS_TITLE
    IS_ASCII


cdef enum:
    NORM
    SHAPE
    LAST3

from spacy.lexeme cimport LexID
from spacy.lexeme cimport StringHash

cpdef bint is_alpha(LexID lex_id) except *
cpdef bint is_digit(LexID lex_id) except *
cpdef bint is_punct(LexID lex_id) except *
cpdef bint is_space(LexID lex_id) except *
cpdef bint is_lower(LexID lex_id) except *
cpdef bint is_upper(LexID lex_id) except *
cpdef bint is_title(LexID lex_id) except *
cpdef bint is_ascii(LexID lex_id) except *


cpdef StringHash norm_of(LexID lex_id) except 0
cpdef StringHash shape_of(LexID lex_id) except 0
cpdef StringHash last3_of(LexID lex_id) except 0
