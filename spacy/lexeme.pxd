from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t

# Put these above import to avoid circular import problem
ctypedef int ClusterID
ctypedef uint32_t StringHash
ctypedef size_t Lexeme_addr
ctypedef char Bits8
ctypedef uint64_t Bits64


cdef struct Orthography:
    StringHash last3
    StringHash shape
    StringHash norm

    size_t length
    unsigned char first
    Bits8 flags


cdef struct Distribution:
    double prob
    ClusterID cluster
    Bits64 tagdict
    Bits8 flags


cdef struct Lexeme:
    StringHash sic # Hash of the original string
    StringHash lex # Hash of the word, with punctuation and clitics split off

    Distribution* dist # Distribution info, lazy loaded
    Orthography* orth  # Extra orthographic views
    Lexeme* tail # Lexemes are linked lists, to deal with sub-tokens


cdef Lexeme BLANK_WORD = Lexeme(0, 0, NULL, NULL, NULL)


cdef enum StringAttr:
    SIC
    LEX
    NORM
    SHAPE
    LAST3
    LENGTH


cpdef StringHash attr_of(size_t lex_id, StringAttr attr) except 0

cpdef StringHash sic_of(size_t lex_id) except 0
cpdef StringHash lex_of(size_t lex_id) except 0
cpdef StringHash norm_of(size_t lex_id) except 0
cpdef StringHash shape_of(size_t lex_id) except 0
cpdef StringHash last3_of(size_t lex_id) except 0
cpdef StringHash length_of(size_t lex_id)
