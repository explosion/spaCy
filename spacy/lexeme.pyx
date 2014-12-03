from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64

from libc.string cimport memset

import orth


memset(&EMPTY_LEXEME, 0, sizeof(Lexeme))


cpdef Lexeme init(id_t i, unicode string, hash_t hashed,
                  StringStore string_store, dict props) except *:
    cdef Lexeme lex
    lex.id = i
    lex.length = len(string)
    lex.sic = string_store[string]
    
    lex.cluster = props.get('cluster', 0)
    lex.pos_type = props.get('pos_type', 0)
    lex.sense_type = props.get('sense_type', 0)
    lex.prob = props.get('prob', 0)

    lex.upper_pc = props.get('upper_pc', 0.0)
    lex.title_pc = props.get('lower_pc', 0.0)

    lex.prefix = string_store[string[:1]]
    lex.suffix = string_store[string[-3:]]
    lex.norm = lex.sic # TODO
    lex.shape = string_store[orth.word_shape(string)]
    lex.asciied = string_store[orth.asciied(string)]
   
    lex.flags = props.get('flags', 0)
    return lex


cdef attr_t get_attr(const Lexeme* lex, attr_id_t feat_name):
    if feat_name < (sizeof(flags_t) * 8):
        return check_flag(lex, feat_name)
    elif feat_name == ID:
        return lex.id
    elif feat_name == SIC:
        return lex.sic
    elif feat_name == NORM:
        return lex.norm
    elif feat_name == SHAPE:
        return lex.shape
    elif feat_name == ASCIIED:
        return lex.asciied
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
    elif feat_name == SENSE_TYPE:
        return lex.sense_type
    else:
        raise StandardError('Feature ID: %d not found' % feat_name)
