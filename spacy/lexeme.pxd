from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t

# Put these above import to avoid circular import problem
ctypedef int ClusterID
ctypedef uint32_t StringHash
ctypedef size_t Lexeme_addr
ctypedef char Bits8
ctypedef uint64_t Bits64


cdef enum OrthFlag:
    IS_ALPHA
    IS_DIGIT
    IS_PUNCT
    IS_WHITE
    IS_LOWER
    IS_UPPER
    IS_TITLE
    IS_ASCII


cdef enum DistFlag:
    OFT_UPPER
    OFT_TITLE
    DIST_FLAG3
    DIST_FLAG4
    DIST_FLAG5
    DIST_FLAG6
    DIST_FLAG7
    DIST_FLAG8


cdef struct Orthography:
    StringHash last3
    StringHash shape
    StringHash norm

    size_t length
    Py_UNICODE first
    Bits8 flags


cdef struct Distribution:
    double prob
    ClusterID cluster
    Bits64 tagdict
    Bits8 flags


cdef struct Lexeme:
    StringHash lex # Hash of the word
    Orthography* orth  # Extra orthographic views
    Distribution* dist # Distribution info


cdef Lexeme BLANK_WORD = Lexeme(0, NULL, NULL)


cdef enum StringAttr:
    LEX
    NORM
    SHAPE
    LAST3
    LENGTH


cpdef StringHash attr_of(size_t lex_id, StringAttr attr) except 0

cpdef StringHash lex_of(size_t lex_id) except 0

cpdef StringHash norm_of(size_t lex_id) except 0
cpdef StringHash shape_of(size_t lex_id) except 0
cpdef StringHash last3_of(size_t lex_id) except 0

cpdef size_t length_of(size_t lex_id) except *
cpdef Py_UNICODE first_of(size_t lex_id) except *

cpdef double prob_of(size_t lex_id) except 0
cpdef ClusterID cluster_of(size_t lex_id) except 0

cpdef bint check_orth_flag(size_t lex, OrthFlag flag) except *
cpdef bint check_dist_flag(size_t lex, DistFlag flag) except *
