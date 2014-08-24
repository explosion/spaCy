from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t

ctypedef int ClusterID
ctypedef uint32_t StringHash
ctypedef size_t LexID
ctypedef char OrthFlags
ctypedef char DistFlags
ctypedef uint64_t TagFlags


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


cdef class Word:
    # NB: the readonly keyword refers to _Python_ access. The attributes are
    # writeable from Cython.
    cdef readonly StringHash lex
    cdef readonly char* string
    cdef readonly size_t length
    cdef readonly double prob
    cdef readonly ClusterID cluster
    cdef readonly TagFlags possible_tags
    cdef readonly DistFlags dist_flags
    cdef readonly OrthFlags orth_flags
    cdef StringHash* string_views

    cpdef StringHash get_view(self, size_t i) except 0

    cpdef bint can_tag(self, TagFlags flag) except *
    cpdef bint check_dist_flag(self, DistFlags flag) except *
    cpdef bint check_orth_flag(self, OrthFlags flag) except *

    cpdef bint is_often_titled(self) except *
    cpdef bint is_often_uppered(self) except *

    cpdef bint is_alpha(self) except *
    cpdef bint is_digit(self) except *
    cpdef bint is_punct(self) except *
    cpdef bint is_space(self) except *
    cpdef bint is_lower(self) except *
    cpdef bint is_upper(self) except *
    cpdef bint is_title(self) except *
    cpdef bint is_ascii(self) except *
