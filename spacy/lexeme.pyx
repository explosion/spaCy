from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64

from libc.string cimport memset

from .orth cimport word_shape
from .typedefs cimport attr_t


memset(&EMPTY_LEXEME, 0, sizeof(LexemeC))


cdef int set_lex_struct_props(LexemeC* lex, dict props, StringStore string_store) except -1:

    lex.length = props['length']
    lex.sic = string_store[props['sic']]
    lex.norm1 = string_store[props['norm1']] 
    lex.norm2 = string_store[props['norm2']] 
    lex.shape = string_store[props['shape']] 
    lex.prefix = string_store[props['prefix']]
    lex.suffix = string_store[props['suffix']]
    
    lex.cluster = props['cluster']
    lex.prob = props['prob']
    lex.sentiment = props['sentiment']

    lex.flags = props['flags']


cdef class Lexeme:
    def __init__(self):
        pass
        

cdef Lexeme Lexeme_cinit(const LexemeC* c, StringStore strings):
    cdef Lexeme py = Lexeme.__new__(Lexeme)

    py.vec = c.vec

    py.flags = c.flags
    py.id = c.id
    py.length = c.length

    py.sic = strings[c.sic]
    py.norm1 = strings[c.norm1]
    py.norm2 = strings[c.norm2]
    py.shape = strings[c.shape]
    py.prefix = strings[c.prefix]
    py.suffix = strings[c.suffix]

    py.sic_id = c.sic
    py.norm1_id = c.norm1
    py.norm2_id = c.norm2
    py.shape_id = c.shape
    py.prefix_id = c.prefix
    py.suffix_id = c.suffix
    
    py.cluster = c.cluster

    py.prob = c.prob
    py.sentiment = c.sentiment
    return py
