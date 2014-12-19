from libcpp.vector cimport vector

from cpython cimport Py_UNICODE_ISSPACE, Py_UNICODE_ISALPHA, Py_UNICODE_ISUPPER

from preshed.maps cimport PreshMap
from cymem.cymem cimport Pool

from .typedefs cimport hash_t
from .tokens cimport Tokens, TokenC
from .lexeme cimport Lexeme
from .tagger cimport Tagger
from .utf8string cimport StringStore, UniStr
from .morphology cimport Morphologizer
from .syntax.parser cimport GreedyParser


cdef union LexemesOrTokens:
    const Lexeme* const* lexemes
    TokenC* tokens


cdef struct Cached:
    LexemesOrTokens data
    bint is_lex
    int length


cdef class Lexicon:
    cpdef public get_lex_props
    cdef Pool mem
    cpdef readonly StringStore strings
    cdef vector[Lexeme*] lexemes

    cdef const Lexeme* get(self, Pool mem, UniStr* s) except NULL
    
    cdef PreshMap _map
    

cdef class Language:
    cdef Pool mem
    cdef readonly unicode name
    cdef PreshMap _cache
    cdef PreshMap _specials
    cpdef readonly Lexicon lexicon
    cpdef readonly Tagger pos_tagger
    cpdef readonly Morphologizer morphologizer
    cpdef readonly GreedyParser parser

    cdef object _prefix_re
    cdef object _suffix_re
    cdef object _infix_re

    cpdef Tokens tokens_from_list(self, list strings)
    cpdef Tokens tokenize(self, unicode text)


    cdef int _try_cache(self, int idx, hash_t key, Tokens tokens) except -1
    cdef int _tokenize(self, Tokens tokens, UniStr* span, int start, int end) except -1
    cdef UniStr* _split_affixes(self, UniStr* string, vector[Lexeme*] *prefixes,
                             vector[Lexeme*] *suffixes) except NULL
    cdef int _attach_tokens(self, Tokens tokens, int idx, UniStr* string,
                            vector[Lexeme*] *prefixes, vector[Lexeme*] *suffixes) except -1
    cdef int _find_prefix(self, Py_UNICODE* characters, size_t length) except -1
    cdef int _find_suffix(self, Py_UNICODE* characters, size_t length) except -1
    cdef int _find_infix(self, Py_UNICODE* characters, size_t length) except -1
    cdef int _save_cached(self, const TokenC* tokens, hash_t key, int n) except -1

    cdef int is_base_np_end(self, const TokenC* token) except -1
    cdef int is_outside_base_np(self, const TokenC* token) except -1
 
