from libcpp.vector cimport vector

from preshed.maps cimport PreshMap
from cymem.cymem cimport Pool

from .typedefs cimport hash_t
from .tokens cimport Tokens
from .lexeme cimport Lexeme
from .tagger cimport Tagger
from .ner.greedy_parser cimport NERParser
from .utf8string cimport StringStore


cdef extern from "Python.h":
    cdef bint Py_UNICODE_ISSPACE(Py_UNICODE ch)
    cdef bint Py_UNICODE_ISALNUM(Py_UNICODE ch)
    cdef bint Py_UNICODE_ISALPHA(Py_UNICODE ch)
    cdef bint Py_UNICODE_ISUPPER(Py_UNICODE ch)


cdef struct String:
    Py_UNICODE* chars
    size_t n
    hash_t key


cdef class Lexicon:
    cdef Pool mem
    cpdef readonly size_t size
    cpdef readonly StringStore strings
    cdef vector[Lexeme*] lexemes

    cdef Lexeme* get(self, String* s) except NULL
    
    cdef PreshMap _dict
    

cdef class Language:
    cdef Pool mem
    cdef readonly unicode name
    cdef PreshMap _cache
    cdef PreshMap _specials
    cpdef readonly Lexicon lexicon

    cpdef readonly Tagger pos_tagger
    cpdef readonly NERParser ner_tagger

    cdef object _prefix_re
    cdef object _suffix_re
    cdef object _infix_re

    cpdef Tokens tokens_from_list(self, list strings)
    cpdef Tokens tokenize(self, unicode text)

    cdef int _tokenize(self, Tokens tokens, String* span, int start, int end) except -1
    cdef String* _split_affixes(self, String* string, vector[Lexeme*] *prefixes,
                             vector[Lexeme*] *suffixes) except NULL
    cdef int _attach_tokens(self, Tokens tokens, int idx, String* string,
                            vector[Lexeme*] *prefixes, vector[Lexeme*] *suffixes) except -1
    cdef int _find_prefix(self, Py_UNICODE* characters, size_t length) except -1
    cdef int _find_suffix(self, Py_UNICODE* characters, size_t length) except -1
    cdef int _find_infix(self, Py_UNICODE* characters, size_t length) except -1
    cdef int _save_cached(self, Lexeme** tokens, hash_t key, int n) except -1
 
