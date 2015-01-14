from .typedefs cimport hash_t, flags_t, id_t, len_t, tag_t, attr_t, attr_id_t
from .typedefs cimport ID, SIC, NORM1, NORM2, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER
from .structs cimport LexemeC
from .strings cimport StringStore


cdef LexemeC EMPTY_LEXEME


cdef int set_lex_struct_props(LexemeC* lex, dict props, StringStore strings) except -1
 
cdef class Lexeme:
    cdef const float* vec

    cdef readonly flags_t flags
    cdef readonly attr_t id
    cdef readonly attr_t length

    cdef readonly attr_t sic
    cdef readonly unicode norm1
    cdef readonly unicode norm2
    cdef readonly unicode shape
    cdef readonly unicode prefix
    cdef readonly unicode suffix

    cdef readonly attr_t sic_id
    cdef readonly attr_t norm1_id
    cdef readonly attr_t norm2_id
    cdef readonly attr_t shape_id
    cdef readonly attr_t prefix_id
    cdef readonly attr_t suffix_id

    cdef readonly attr_t cluster
    cdef readonly float prob
    cdef readonly float sentiment


cdef Lexeme Lexeme_cinit(const LexemeC* c, StringStore strings)


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
