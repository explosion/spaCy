from .typedefs cimport attr_t, hash_t, flags_t, len_t, tag_t
from .attrs cimport attr_id_t
from .attrs cimport ID, ORTH, LOWER, NORM, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER

from .structs cimport LexemeC
from .strings cimport StringStore

from numpy cimport ndarray


cdef LexemeC EMPTY_LEXEME

cdef class Lexeme:
    cdef LexemeC* c
    cdef readonly Vocab vocab
    cdef readonly attr_t orth

    cdef int set_struct_props(Vocab vocab, LexemeC* lex, dict props) except -1:
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
        lex.repvec = empty_vec

    @staticmethod
    cdef inline attr_t get_struct_attr(const LexemeC* lex, attr_id_t feat_name) nogil:
        if feat_name < (sizeof(flags_t) * 8):
            return Lexeme.check_flag(lex, feat_name)
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

    cdef inline bint check_flag(const LexemeC* lexeme, attr_id_t flag_id) nogil:
        return lexeme.flags & (1 << flag_id)
