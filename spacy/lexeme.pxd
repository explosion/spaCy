from .typedefs cimport hash_t, flags_t, id_t, len_t, tag_t, attr_t

from .utf8string cimport StringStore


# Reserve 64 values for flag features
cpdef enum attr_id_t:
    FLAG0
    FLAG1
    FLAG2
    FLAG3
    FLAG4
    FLAG5
    FLAG6
    FLAG7
    FLAG8
    FLAG9
    FLAG10
    FLAG11
    FLAG12
    FLAG13
    FLAG14
    FLAG15
    FLAG16
    FLAG17
    FLAG18
    FLAG19
    FLAG20
    FLAG21
    FLAG22
    FLAG23
    FLAG24
    FLAG25
    FLAG26
    FLAG27
    FLAG28
    FLAG29
    FLAG30
    FLAG31
    FLAG32
    FLAG33
    FLAG34
    FLAG35
    FLAG36
    FLAG37
    FLAG38
    FLAG39
    FLAG40
    FLAG41
    FLAG42
    FLAG43
    FLAG44
    FLAG45
    FLAG46
    FLAG47
    FLAG48
    FLAG49
    FLAG50
    FLAG51
    FLAG52
    FLAG53
    FLAG54
    FLAG55
    FLAG56
    FLAG57
    FLAG58
    FLAG59
    FLAG60
    FLAG61
    FLAG62
    FLAG63

    ID
    SIC
    DENSE
    SHAPE
    PREFIX
    SUFFIX

    LENGTH
    CLUSTER
    POS_TYPE
    LEMMA


cdef struct Lexeme:
    flags_t flags
   
    attr_t id
    attr_t sic
    attr_t dense
    attr_t shape
    attr_t prefix
    attr_t suffix
 
    attr_t length
    attr_t cluster
    attr_t pos_type

    float prob
    float sentiment


cdef Lexeme EMPTY_LEXEME


cpdef Lexeme init(id_t i, unicode string, hash_t hashed, StringStore store,
                  dict props) except *
 

cdef inline bint check_flag(const Lexeme* lexeme, attr_id_t flag_id) nogil:
    return lexeme.flags & (1 << flag_id)


cdef inline attr_t get_attr(const Lexeme* lex, attr_id_t feat_name) nogil:
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
