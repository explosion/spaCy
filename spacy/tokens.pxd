from cymem.cymem cimport Pool

from .lexeme cimport Lexeme
from .typedefs cimport flag_t
from .utf8string cimport StringStore
from .tagger cimport TagType

from thinc.typedefs cimport atom_t


cdef class Tokens:
    cdef Pool mem
    cdef StringStore _string_store

    cdef Lexeme** _lex_ptr
    cdef int* _idx_ptr
    cdef int* _pos_ptr
    cdef int* _ner_ptr
    cdef Lexeme** lex
    cdef int* idx
    cdef int* pos
    cdef int* ner

    cdef int length
    cdef int max_length

    cdef int extend(self, int i, Lexeme** lexemes, int n) except -1
    cdef int push_back(self, int i, Lexeme* lexeme) except -1
    cpdef int set_tag(self, int i, TagType tag_type, int tag) except -1


cdef class Token:
    cdef StringStore _string_store
    cdef public int i
    cdef public int idx
    cdef public int pos
    cdef public int ner

    cdef public atom_t id
    cdef public atom_t cluster
    cdef public atom_t length
    cdef public atom_t postype
    cdef public atom_t sensetype

    cdef public atom_t sic
    cdef public atom_t norm
    cdef public atom_t shape
    cdef public atom_t asciied
    cdef public atom_t prefix
    cdef public atom_t suffix

    cdef public float prob

    cdef public flag_t flags
