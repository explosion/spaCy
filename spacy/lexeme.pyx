from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64

from libc.string cimport memset

from .orth cimport word_shape


memset(&EMPTY_LEXEME, 0, sizeof(LexemeC))


cdef LexemeC init(id_t i, unicode string, hash_t hashed,
                  StringStore string_store, dict props) except *:
    cdef LexemeC lex
    lex.id = i
    lex.length = len(string)
    lex.sic = string_store[string]
    
    lex.cluster = props.get('cluster', 0)
    lex.prob = props.get('prob', 0)

    lex.prefix = string_store[string[:1]]
    lex.suffix = string_store[string[-3:]]
    lex.shape = string_store[word_shape(string)]
   
    lex.flags = props.get('flags', 0)
    return lex


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
