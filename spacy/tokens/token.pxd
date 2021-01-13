from numpy cimport ndarray
from ..vocab cimport Vocab
from ..structs cimport TokenC
from ..attrs cimport *
from ..typedefs cimport attr_t, flags_t
from ..parts_of_speech cimport univ_pos_t
from .doc cimport Doc
from ..lexeme cimport Lexeme

from ..errors import Errors

cdef int MISSING_DEP = 0

cdef class Token:
    cdef readonly Vocab vocab
    cdef TokenC* c
    cdef readonly int i
    cdef readonly Doc doc

    @staticmethod
    cdef inline Token cinit(Vocab vocab, const TokenC* token, int offset, Doc doc):
        if offset < 0 or offset >= doc.length:
            raise IndexError(Errors.E040.format(i=offset, max_length=doc.length))
        cdef Token self = Token.__new__(Token, vocab, doc, offset)
        return self

    #cdef inline TokenC struct_from_attrs(Vocab vocab, attrs):
    #    cdef TokenC token
    #    attrs = normalize_attrs(attrs)

    cpdef bint check_flag(self, attr_id_t flag_id) except -1

    @staticmethod
    cdef inline attr_t get_struct_attr(const TokenC* token, attr_id_t feat_name) nogil:
        if feat_name < (sizeof(flags_t) * 8):
            return Lexeme.c_check_flag(token.lex, feat_name)
        elif feat_name == LEMMA:
            return token.lemma
        elif feat_name == NORM:
            if token.norm == 0:
                return token.lex.norm
            else:
                return token.norm
        elif feat_name == POS:
            return token.pos
        elif feat_name == TAG:
            return token.tag
        elif feat_name == MORPH:
            return token.morph
        elif feat_name == DEP:
            return token.dep
        elif feat_name == HEAD:
            return token.head
        elif feat_name == SPACY:
            return token.spacy
        elif feat_name == ENT_IOB:
            return token.ent_iob
        elif feat_name == ENT_TYPE:
            return token.ent_type
        elif feat_name == ENT_ID:
            return token.ent_id
        elif feat_name == ENT_KB_ID:
            return token.ent_kb_id
        elif feat_name == SENT_START:
            return token.sent_start
        else:
            return Lexeme.get_struct_attr(token.lex, feat_name)

    @staticmethod
    cdef inline attr_t set_struct_attr(TokenC* token, attr_id_t feat_name,
                                       attr_t value) nogil:
        if feat_name == LEMMA:
            token.lemma = value
        elif feat_name == NORM:
            token.norm = value
        elif feat_name == POS:
            token.pos = <univ_pos_t>value
        elif feat_name == TAG:
            token.tag = value
        elif feat_name == MORPH:
            token.morph = value
        elif feat_name == DEP:
            token.dep = value
        elif feat_name == HEAD:
            token.head = value
        elif feat_name == SPACY:
            token.spacy = value
        elif feat_name == ENT_IOB:
            token.ent_iob = value
        elif feat_name == ENT_TYPE:
            token.ent_type = value
        elif feat_name == ENT_ID:
            token.ent_id = value
        elif feat_name == ENT_KB_ID:
            token.ent_kb_id = value
        elif feat_name == SENT_START:
            token.sent_start = value


    @staticmethod
    cdef inline int missing_dep(const TokenC* token) nogil:
        return token.dep == MISSING_DEP


    @staticmethod
    cdef inline int missing_head(const TokenC* token) nogil:
        return Token.missing_dep(token)
