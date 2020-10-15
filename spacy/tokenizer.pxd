from libcpp.vector cimport vector
from preshed.maps cimport PreshMap
from cymem.cymem cimport Pool

from .typedefs cimport hash_t
from .structs cimport LexemeC, SpanC, TokenC
from .strings cimport StringStore
from .tokens.doc cimport Doc
from .vocab cimport Vocab, LexemesOrTokens, _Cached
from .matcher.phrasematcher cimport PhraseMatcher


cdef class Tokenizer:
    cdef Pool mem
    cdef PreshMap _cache
    cdef PreshMap _specials
    cpdef readonly Vocab vocab

    cdef object _token_match
    cdef object _url_match
    cdef object _prefix_search
    cdef object _suffix_search
    cdef object _infix_finditer
    cdef object _rules
    cdef PhraseMatcher _special_matcher
    cdef int _property_init_count
    cdef int _property_init_max

    cdef Doc _tokenize_affixes(self, unicode string, bint with_special_cases)
    cdef int _apply_special_cases(self, Doc doc) except -1
    cdef void _filter_special_spans(self, vector[SpanC] &original,
                            vector[SpanC] &filtered, int doc_len) nogil
    cdef object _prepare_special_spans(self, Doc doc,
                                       vector[SpanC] &filtered)
    cdef int _retokenize_special_spans(self, Doc doc, TokenC* tokens,
                                       object span_data)
    cdef int _try_specials_and_cache(self, hash_t key, Doc tokens,
                                     int* has_special,
                                     bint with_special_cases) except -1
    cdef int _tokenize(self, Doc tokens, unicode span, hash_t key,
                       int* has_special, bint with_special_cases) except -1
    cdef unicode _split_affixes(self, Pool mem, unicode string,
                                vector[LexemeC*] *prefixes,
                                vector[LexemeC*] *suffixes, int* has_special,
                                bint with_special_cases)
    cdef int _attach_tokens(self, Doc tokens, unicode string,
                            vector[LexemeC*] *prefixes,
                            vector[LexemeC*] *suffixes, int* has_special,
                            bint with_special_cases) except -1
    cdef int _save_cached(self, const TokenC* tokens, hash_t key,
                          int* has_special, int n) except -1
