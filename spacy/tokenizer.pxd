from libcpp.vector cimport vector

from preshed.maps cimport PreshMap
from cymem.cymem cimport Pool

from .typedefs cimport hash_t
from .structs cimport LexemeC, TokenC
from .strings cimport StringStore
from .tokens.doc cimport Doc
from .vocab cimport Vocab, LexemesOrTokens, _Cached


cdef class Tokenizer:
    cdef Pool mem
    cdef PreshMap _cache
    cdef PreshMap _specials
    cpdef readonly Vocab vocab

    cdef public object prefix_search
    cdef public object suffix_search
    cdef public object infix_finditer
    cdef object _rules

    cpdef Doc tokens_from_list(self, list strings)

    cdef int _try_cache(self, hash_t key, Doc tokens) except -1
    cdef int _tokenize(self, Doc tokens, unicode span, hash_t key) except -1
    cdef unicode _split_affixes(self, Pool mem, unicode string, vector[LexemeC*] *prefixes,
                             vector[LexemeC*] *suffixes)
    cdef int _attach_tokens(self, Doc tokens, unicode string,
                            vector[LexemeC*] *prefixes, vector[LexemeC*] *suffixes) except -1

    cdef int _save_cached(self, const TokenC* tokens, hash_t key, int n) except -1
