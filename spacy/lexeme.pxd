from .typedefs cimport attr_t, hash_t, flags_t, len_t, tag_t
from .attrs cimport attr_id_t
from .attrs cimport ID, ORTH, LOWER, NORM, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER

from .structs cimport LexemeC
from .strings cimport StringStore
from .vocab cimport Vocab

from numpy cimport ndarray


cdef LexemeC EMPTY_LEXEME

cdef class Lexeme:
    cdef LexemeC* c
    cdef readonly Vocab vocab
    cdef readonly attr_t orth

    @staticmethod
    cdef inline int set_struct_props(Vocab vocab, LexemeC* lex, dict props) except -1:
        lex.length = props['length']
        lex.orth = vocab.strings[props['orth']]
        lex.lower = vocab.strings[props['lower']]
        lex.norm = vocab.strings[props['norm']]
        lex.shape = vocab.strings[props['shape']]
        lex.prefix = vocab.strings[props['prefix']]
        lex.suffix = vocab.strings[props['suffix']]

        lex.cluster = props['cluster']
        lex.prob = props['prob']
        lex.sentiment = props['sentiment']

        lex.flags = props['flags']

    @staticmethod
    cdef inline attr_t get_struct_attr(const LexemeC* lex, attr_id_t feat_name) nogil:
        if feat_name < (sizeof(flags_t) * 8):
            if Lexeme.check_flag(lex, feat_name):
                return 1
            else:
                return 0
        elif feat_name == ID:
            return lex.id
        elif feat_name == ORTH:
            return lex.orth
        elif feat_name == LOWER:
            return lex.lower
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
    
    @staticmethod
    cdef inline void set_struct_attr(LexemeC* lex, attr_id_t name, attr_t value) nogil:
        if name < (sizeof(flags_t) * 8):
            Lexeme.set_flag(lex, name, value)
        elif name == ID:
            lex.id = value
        elif name == LOWER:
            lex.lower = value
        elif name == NORM:
            lex.norm = value
        elif name == SHAPE:
            lex.shape = value
        elif name == PREFIX:
            lex.prefix = value
        elif name == SUFFIX:
            lex.suffix = value
        elif name == CLUSTER:
            lex.cluster = value

    @staticmethod
    cdef inline bint check_flag(const LexemeC* lexeme, attr_id_t flag_id) nogil:
        if lexeme.flags & (1 << flag_id):
            return True
        else:
            return False

    @staticmethod
    cdef inline bint set_flag(LexemeC* lex, attr_id_t flag_id, int value) nogil:
        cdef flags_t one = 1
        if value:
            lex.flags |= one << flag_id
        else:
            lex.flags &= ~(one << flag_id)
