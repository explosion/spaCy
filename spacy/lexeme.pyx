# cython: embedsignature=True
from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64

from libc.string cimport memset

from .orth cimport word_shape
from .typedefs cimport attr_t, flags_t
import numpy


memset(&EMPTY_LEXEME, 0, sizeof(LexemeC))


cdef int set_lex_struct_props(LexemeC* lex, dict props, StringStore string_store,
                              const float* empty_vec) except -1:
    lex.length = props['length']
    lex.orth = string_store[props['orth']]
    lex.lower = string_store[props['lower']]
    lex.norm = string_store[props['norm']]
    lex.shape = string_store[props['shape']]
    lex.prefix = string_store[props['prefix']]
    lex.suffix = string_store[props['suffix']]

    lex.cluster = props['cluster']
    lex.prob = props['prob']
    lex.sentiment = props['sentiment']

    lex.flags = props['flags']
    lex.repvec = empty_vec


cdef class Lexeme:
    """An entry in the vocabulary.  A Lexeme has no string context --- it's a
    word-type, as opposed to a word token.  It therefore has no part-of-speech
    tag, dependency parse, or lemma (lemmatization depends on the part-of-speech
    tag).
    """
    def __cinit__(self, int vec_size):
        self.repvec = numpy.ndarray(shape=(vec_size,), dtype=numpy.float32)

    @property
    def has_repvec(self):
        return self.l2_norm != 0

    cpdef bint check(self, attr_id_t flag_id) except -1:
        return self.flags & (1 << flag_id)

    cpdef bint has_sense(self, flags_t flag_id) except -1:
        return self.senses & (1 << flag_id)
