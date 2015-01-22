# cython: embedsignature=True
from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64

from libc.string cimport memset

from .orth cimport word_shape
from .typedefs cimport attr_t
import numpy


memset(&EMPTY_LEXEME, 0, sizeof(LexemeC))


cdef int set_lex_struct_props(LexemeC* lex, dict props, StringStore string_store,
                              const float* empty_vec) except -1:
    lex.length = props['length']
    lex.orth = string_store[props['orth']]
    lex.norm1 = string_store[props['norm1']] 
    lex.norm2 = string_store[props['norm2']] 
    lex.shape = string_store[props['shape']] 
    lex.prefix = string_store[props['prefix']]
    lex.suffix = string_store[props['suffix']]
    
    lex.cluster = props['cluster']
    lex.prob = props['prob']
    lex.sentiment = props['sentiment']

    lex.flags = props['flags']
    lex.repvec = empty_vec


cdef class Lexeme:
    """A dummy docstring"""
    def __cinit__(self, int vec_size):
        self.repvec = numpy.ndarray(shape=(vec_size,), dtype=numpy.float32)
