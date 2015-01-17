from libcpp.vector cimport vector

from cpython cimport Py_UNICODE_ISSPACE, Py_UNICODE_ISALPHA, Py_UNICODE_ISUPPER

from preshed.maps cimport PreshMap
from cymem.cymem cimport Pool

from .typedefs cimport hash_t
from .structs cimport LexemeC, TokenC, Morphology, UniStr
from .strings cimport StringStore
from .tokens cimport Tokens
from .vocab cimport Vocab, _Cached


cdef union LexemesOrTokens:
    const LexemeC* const* lexemes
    TokenC* tokens


cdef class Tokenizer:
    cdef Pool mem
    cdef PreshMap _cache
    cdef PreshMap _specials
    cpdef readonly Vocab vocab

    cdef object _prefix_re
    cdef object _suffix_re
    cdef object _infix_re

    cpdef Tokens tokens_from_list(self, list strings)

    cdef int _try_cache(self, int idx, hash_t key, Tokens tokens) except -1
    cdef int _tokenize(self, Tokens tokens, UniStr* span, int start, int end) except -1
    cdef UniStr* _split_affixes(self, UniStr* string, vector[LexemeC*] *prefixes,
                             vector[LexemeC*] *suffixes) except NULL
    cdef int _attach_tokens(self, Tokens tokens, int idx, UniStr* string,
                            vector[LexemeC*] *prefixes, vector[LexemeC*] *suffixes) except -1
    cdef int _find_prefix(self, Py_UNICODE* characters, size_t length) except -1
    cdef int _find_suffix(self, Py_UNICODE* characters, size_t length) except -1
    cdef int _find_infix(self, Py_UNICODE* characters, size_t length) except -1
    cdef int _save_cached(self, const TokenC* tokens, hash_t key, int n) except -1
