from cymem.cymem cimport Pool
from libcpp.vector cimport vector
from preshed.maps cimport PreshMap

from .matcher.phrasematcher cimport PhraseMatcher
from .strings cimport StringStore
from .structs cimport LexemeC, SpanC, TokenC
from .tokens.doc cimport Doc
from .typedefs cimport hash_t
from .vocab cimport LexemesOrTokens, Vocab, _Cached


cdef class Tokenizer:
    cdef Pool mem
    cdef PreshMap _cache
    cdef PreshMap _specials
    cdef readonly Vocab vocab

    cdef object _token_match
    cdef object _url_match
    cdef object _prefix_search
    cdef object _suffix_search
    cdef object _infix_finditer
    cdef object _rules
    cdef PhraseMatcher _special_matcher
    # TODO convert to bool in v4
    cdef int _faster_heuristics
    # TODO next one is unused and should be removed in v4
    # https://github.com/explosion/spaCy/pull/9150
    cdef int _unused_int2

    cdef Doc _tokenize_affixes(self, str string, bint with_special_cases)
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
    cdef int _tokenize(self, Doc tokens, str span, hash_t key,
                       int* has_special, bint with_special_cases) except -1
    cdef str _split_affixes(self, Pool mem, str string,
                                vector[LexemeC*] *prefixes,
                                vector[LexemeC*] *suffixes, int* has_special,
                                bint with_special_cases)
    cdef int _attach_tokens(self, Doc tokens, str string,
                            vector[LexemeC*] *prefixes,
                            vector[LexemeC*] *suffixes, int* has_special,
                            bint with_special_cases) except -1
    cdef int _save_cached(self, const TokenC* tokens, hash_t key,
                          int* has_special, int n) except -1
