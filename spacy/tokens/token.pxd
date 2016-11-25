from numpy cimport ndarray
from ..vocab cimport Vocab
from ..structs cimport TokenC
from ..attrs cimport *
from ..typedefs cimport attr_t, flags_t
from .doc cimport Doc
from ..lexeme cimport Lexeme


cdef class Token:
    cdef readonly Vocab vocab
    cdef TokenC* c
    cdef readonly int i
    cdef readonly Doc doc

    @staticmethod
    cdef inline Token cinit(Vocab vocab, const TokenC* token, int offset, Doc doc):
        if offset < 0 or offset >= doc.length:
            msg = "Attempt to access token at %d, max length %d"
            raise IndexError(msg % (offset, doc.length))
        if doc._py_tokens[offset] != None:
            return doc._py_tokens[offset]
        cdef Token self = Token.__new__(Token, vocab, doc, offset)
        doc._py_tokens[offset] = self
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
        elif feat_name == POS:
            return token.pos
        elif feat_name == TAG:
            return token.tag
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
        else:
            return Lexeme.get_struct_attr(token.lex, feat_name)
