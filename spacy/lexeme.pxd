from numpy cimport ndarray

from .attrs cimport (
    ID,
    LANG,
    LENGTH,
    LOWER,
    NORM,
    ORTH,
    PREFIX,
    SHAPE,
    SUFFIX,
    attr_id_t,
)
from .strings cimport StringStore
from .structs cimport LexemeC
from .typedefs cimport attr_t, flags_t, hash_t, len_t, tag_t
from .vocab cimport Vocab


cdef LexemeC EMPTY_LEXEME
cdef attr_t OOV_RANK

cdef class Lexeme:
    cdef LexemeC* c
    cdef readonly Vocab vocab
    cdef readonly attr_t orth

    @staticmethod
    cdef inline Lexeme from_ptr(LexemeC* lex, Vocab vocab):
        cdef Lexeme self = Lexeme.__new__(Lexeme, vocab, lex.orth)
        self.c = lex
        self.vocab = vocab
        self.orth = lex.orth
        return self

    @staticmethod
    cdef inline void set_struct_attr(LexemeC* lex, attr_id_t name, attr_t value) noexcept nogil:
        if name < (sizeof(flags_t) * 8):
            Lexeme.c_set_flag(lex, name, value)
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
        elif name == LANG:
            lex.lang = value

    @staticmethod
    cdef inline attr_t get_struct_attr(const LexemeC* lex, attr_id_t feat_name) noexcept nogil:
        if feat_name < (sizeof(flags_t) * 8):
            if Lexeme.c_check_flag(lex, feat_name):
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
        elif feat_name == LANG:
            return lex.lang
        else:
            return 0

    @staticmethod
    cdef inline bint c_check_flag(const LexemeC* lexeme, attr_id_t flag_id) noexcept nogil:
        cdef flags_t one = 1
        if lexeme.flags & (one << flag_id):
            return True
        else:
            return False

    @staticmethod
    cdef inline bint c_set_flag(LexemeC* lex, attr_id_t flag_id, bint value) noexcept nogil:
        cdef flags_t one = 1
        if value:
            lex.flags |= one << flag_id
        else:
            lex.flags &= ~(one << flag_id)
