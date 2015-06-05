from .typedefs cimport hash_t, flags_t, id_t, len_t, tag_t, attr_t, attr_id_t
from .typedefs cimport ID, ORTH, LOWER, NORM, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER
from .structs cimport LexemeC
from .strings cimport StringStore

from numpy cimport ndarray



cdef LexemeC EMPTY_LEXEME


cdef int set_lex_struct_props(LexemeC* lex, dict props, StringStore strings,
                              const float* empty_vec) except -1

cdef class Lexeme:
    cdef readonly ndarray repvec

    cdef readonly flags_t flags
    cdef readonly attr_t id
    cdef readonly attr_t length

    cdef readonly attr_t orth
    cdef readonly attr_t lower
    cdef readonly attr_t norm
    cdef readonly attr_t shape
    cdef readonly attr_t prefix
    cdef readonly attr_t suffix

    cdef readonly unicode orth_
    cdef readonly unicode lower_
    cdef readonly unicode norm_
    cdef readonly unicode shape_
    cdef readonly unicode prefix_
    cdef readonly unicode suffix_

    cdef readonly attr_t cluster
    cdef readonly float prob
    cdef readonly float sentiment
    cdef readonly float l2_norm

    # Workaround for an apparent bug in the way the decorator is handled ---
    # TODO: post bug report / patch to Cython.
    @staticmethod
    cdef inline Lexeme from_ptr(const LexemeC* ptr, StringStore strings, int repvec_length):
        cdef Lexeme py = Lexeme.__new__(Lexeme, repvec_length)
        for i in range(repvec_length):
            py.repvec[i] = ptr.repvec[i]
        py.l2_norm = ptr.l2_norm
        py.flags = ptr.flags
        py.id = ptr.id
        py.length = ptr.length

        py.orth = ptr.orth
        py.lower = ptr.lower
        py.norm = ptr.norm
        py.shape = ptr.shape
        py.prefix = ptr.prefix
        py.suffix = ptr.suffix

        py.orth_ = strings[ptr.orth]
        py.lower_ = strings[ptr.lower]
        py.norm_ = strings[ptr.norm]
        py.shape_ = strings[ptr.shape]
        py.prefix_ = strings[ptr.prefix]
        py.suffix_ = strings[ptr.suffix]

        py.cluster = ptr.cluster
        py.prob = ptr.prob
        py.sentiment = ptr.sentiment
        return py

    cpdef bint check(self, attr_id_t flag_id) except -1


cdef inline bint check_flag(const LexemeC* lexeme, attr_id_t flag_id) nogil:
    return lexeme.flags & (1 << flag_id)


cdef inline attr_t get_attr(const LexemeC* lex, attr_id_t feat_name) nogil:
    if feat_name < (sizeof(flags_t) * 8):
        return check_flag(lex, feat_name)
    elif feat_name == ID:
        return lex.id
    elif feat_name == ORTH:
        return lex.orth
    elif feat_name == LOWER:
        return lex.norm
    elif feat_name == NORM:
        return lex.norm
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
