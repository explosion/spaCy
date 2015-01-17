from .typedefs cimport hash_t, flags_t, id_t, len_t, tag_t, attr_t, attr_id_t
from .typedefs cimport ID, SIC, NORM1, NORM2, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER
from .structs cimport LexemeC
from .strings cimport StringStore

from numpy cimport ndarray



cdef LexemeC EMPTY_LEXEME


cdef int set_lex_struct_props(LexemeC* lex, dict props, StringStore strings,
                              const float* empty_vec) except -1
 
cdef class Lexeme:
    cdef readonly ndarray vec

    cdef readonly flags_t flags
    cdef readonly attr_t id
    cdef readonly attr_t length

    cdef readonly attr_t sic
    cdef readonly attr_t norm1
    cdef readonly attr_t norm2
    cdef readonly attr_t shape
    cdef readonly attr_t prefix
    cdef readonly attr_t suffix

    cdef readonly unicode sic_
    cdef readonly unicode norm1_
    cdef readonly unicode norm2_
    cdef readonly unicode shape_
    cdef readonly unicode prefix_
    cdef readonly unicode suffix_

    cdef readonly attr_t cluster
    cdef readonly float prob
    cdef readonly float sentiment

    # Workaround for an apparent bug in the way the decorator is handled ---
    # TODO: post bug report / patch to Cython.
    @staticmethod
    cdef inline Lexeme from_ptr(const LexemeC* ptr, StringStore strings):
        cdef Lexeme py = Lexeme.__new__(Lexeme, 300)
        for i in range(300):
            py.vec[i] = ptr.vec[i]
        py.flags = ptr.flags
        py.id = ptr.id
        py.length = ptr.length

        py.sic = ptr.sic
        py.norm1 = ptr.norm1
        py.norm2 = ptr.norm2
        py.shape = ptr.shape
        py.prefix = ptr.prefix
        py.suffix = ptr.suffix

        py.sic_ = strings[ptr.sic]
        py.norm1_ = strings[ptr.norm1]
        py.norm2_ = strings[ptr.norm2]
        py.shape_ = strings[ptr.shape]
        py.prefix_ = strings[ptr.prefix]
        py.suffix_ = strings[ptr.suffix]

        py.cluster = ptr.cluster
        py.prob = ptr.prob
        py.sentiment = ptr.sentiment
        return py


cdef inline bint check_flag(const LexemeC* lexeme, attr_id_t flag_id) nogil:
    return lexeme.flags & (1 << flag_id)


cdef inline attr_t get_attr(const LexemeC* lex, attr_id_t feat_name) nogil:
    if feat_name < (sizeof(flags_t) * 8):
        return check_flag(lex, feat_name)
    elif feat_name == ID:
        return lex.id
    elif feat_name == SIC:
        return lex.sic
    elif feat_name == NORM1:
        return lex.norm1
    elif feat_name == NORM2:
        return lex.norm2
    elif feat_name == SHAPE:
        return lex.shape
    elif feat_name == PREFIX:
        return lex.prefix
    elif feat_name == SUFFIX:
        return lex.suffix
    elif feat_name == LENGTH:
        return lex.length
    elif feat_name == CLUSTER:
        return lex.cluster
    else:
        return 0
