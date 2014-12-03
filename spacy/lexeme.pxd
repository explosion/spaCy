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
    NORM
    SHAPE
    ASCIIED
    PREFIX
    SUFFIX

    LENGTH
    CLUSTER
    POS_TYPE
    SENSE_TYPE


cdef struct Lexeme:
    flags_t flags
   
    attr_t id
    attr_t sic
    attr_t norm
    attr_t shape
    attr_t asciied
    attr_t prefix
    attr_t suffix
 
    attr_t length
    attr_t cluster
    attr_t pos_type
    attr_t sense_type

    float prob
    float upper_pc
    float title_pc


cdef Lexeme EMPTY_LEXEME


cpdef Lexeme init(id_t i, unicode string, hash_t hashed, StringStore store,
                  dict props) except *
 

cdef inline bint check_flag(Lexeme* lexeme, attr_id_t flag_id) nogil:
    return lexeme.flags & (1 << flag_id)


cdef attr_t get_attr(Lexeme* lex, attr_id_t attr_id)
