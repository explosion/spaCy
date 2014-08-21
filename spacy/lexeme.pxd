from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t


ctypedef int ClusterID
ctypedef uint32_t StringHash
ctypedef size_t LexID
ctypedef char OrthFlags
ctypedef char DistFlags
ctypedef uint64_t TagFlags


cdef struct Lexeme:
    StringHash lex
    char* string
    size_t length
    double prob
    ClusterID cluster
    TagFlags possible_tags
    DistFlags dist_flags
    OrthFlags orth_flags
    StringHash* string_views


cpdef StringHash lex_of(LexID lex_id) except 0
cpdef char first_of(LexID lex_id) except 0
cpdef size_t length_of(LexID lex_id) except 0
cpdef double prob_of(LexID lex_id) except 0
cpdef ClusterID cluster_of(LexID lex_id) except 0

cpdef bint check_tag_flag(LexID lex, TagFlags flag) except *
cpdef bint check_dist_flag(LexID lex, DistFlags flag) except *
cpdef bint check_orth_flag(LexID lex, OrthFlags flag) except *

cpdef StringHash view_of(LexID lex_id, size_t view) except 0
