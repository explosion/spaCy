from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t
from libcpp.vector cimport vector
from libc.stdint cimport uint64_t, int64_t

from preshed.maps cimport PreshMap
from cymem.cymem cimport Pool

from .word cimport Lexeme
from .tokens cimport Tokens
from .lexeme cimport LexemeC


cdef extern from "Python.h":
    cdef bint Py_UNICODE_ISSPACE(Py_UNICODE ch)
    cdef bint Py_UNICODE_ISALNUM(Py_UNICODE ch)
    cdef bint Py_UNICODE_ISALPHA(Py_UNICODE ch)
    cdef bint Py_UNICODE_ISUPPER(Py_UNICODE ch)


cdef struct String:
    Py_UNICODE* chars
    size_t n
    uint64_t key


cdef class Lexicon:
    cdef Pool mem
    cpdef readonly size_t size

    cdef vector[LexemeC*] lexemes

    cpdef Lexeme lookup(self, unicode string)
    cdef LexemeC* get(self, String* s) except NULL
    
    cdef PreshMap _dict
    
    cdef list _string_features
    cdef list _flag_features

cdef class Language:
    cdef Pool _mem
    cdef unicode name
    cdef PreshMap cache
    cdef PreshMap specials
    cpdef readonly Lexicon lexicon

    cdef object prefix_re
    cdef object suffix_re
    cdef object infix_re

    cpdef Tokens tokenize(self, unicode text)

    cdef int _tokenize(self, Tokens tokens, String* span, int start, int end) except -1
    cdef String* _split_affixes(self, String* string, vector[LexemeC*] *prefixes,
                             vector[LexemeC*] *suffixes) except NULL
    cdef int _attach_tokens(self, Tokens tokens, int idx, String* string,
                            vector[LexemeC*] *prefixes, vector[LexemeC*] *suffixes) except -1
    cdef int _find_prefix(self, Py_UNICODE* characters, size_t length) except -1
    cdef int _find_suffix(self, Py_UNICODE* characters, size_t length) except -1
    cdef int _find_infix(self, Py_UNICODE* characters, size_t length) except -1
    cdef int _save_cached(self, LexemeC** tokens, uint64_t key, int n) except -1
 
