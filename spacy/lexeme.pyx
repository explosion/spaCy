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
    lex.pos_type = props.get('pos_type', 0)
    lex.prob = props.get('prob', 0)

    lex.prefix = string_store[string[:1]]
    lex.suffix = string_store[string[-3:]]
    lex.shape = string_store[word_shape(string)]
   
    lex.flags = props.get('flags', 0)
    return lex



