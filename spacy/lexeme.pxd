from .typedefs cimport hash_t, flags_t, id_t, len_t, tag_t, attr_t, attr_id_t
from .typedefs cimport ID, SIC, DENSE, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER, POS_TYPE
from .structs cimport LexemeC
from .strings cimport StringStore


cdef LexemeC EMPTY_LEXEME


cdef LexemeC init(id_t i, unicode string, hash_t hashed, StringStore store,
                  dict props) except *
 

cdef inline bint check_flag(const LexemeC* lexeme, attr_id_t flag_id) nogil:
    return lexeme.flags & (1 << flag_id)


cdef inline attr_t get_attr(const LexemeC* lex, attr_id_t feat_name) nogil:
    if feat_name < (sizeof(flags_t) * 8):
        return check_flag(lex, feat_name)
    elif feat_name == ID:
        return lex.id
    elif feat_name == SIC:
        return lex.sic
    elif feat_name == DENSE:
        return lex.dense
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
    elif feat_name == POS_TYPE:
        return lex.pos_type
    else:
        return 0
