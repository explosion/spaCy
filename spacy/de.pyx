# cython: profile=True
# cython: embedsignature=True
'''Tokenize German text, using a scheme based on the Negra corpus.

Tokenization is generally similar to English text, and the same set of orthographic
flags are used.

An abbreviation list is used to handle common abbreviations. Hyphenated words
are not split, following the Treebank usage.
'''
from __future__ import unicode_literals

from libc.stdint cimport uint64_t

cimport spacy

from spacy.orth import is_alpha, is_digit, is_punct, is_space, is_lower, is_ascii
from spacy.orth import canonicalize_case, get_string_shape, asciify, get_non_sparse
from spacy.common cimport check_punct

# Python-readable flag constants --- can't read an enum from Python

# Don't want to manually assign these numbers, or we'll insert one and have to
# change them all.
# Don't use "i", as we don't want it in the global scope!
cdef size_t __i = 0

ALPHA = __i; i += 1
DIGIT = __i; __i += 1
PUNCT = __i; __i += 1
SPACE = __i; __i += 1
LOWER = __i; __i += 1
UPPER = __i; __i += 1
TITLE = __i; __i += 1
ASCII = __i; __i += 1

OFT_LOWER = __i; __i += 1 
OFT_UPPER = __i; __i += 1
OFT_TITLE = __i; __i += 1

PUNCT = __i; __i += 1
CONJ = __i; __i += 1
NUM = __i; __i += 1
X = __i; __i += 1
DET = __i; __i += 1
ADP = __i; __i += 1
ADJ = __i; __i += 1
ADV = __i; __i += 1
VERB = __i; __i += 1
NOUN = __i; __i += 1
PDT = __i; __i += 1
POS = __i; __i += 1
PRON = __i; __i += 1
PRT = __i; __i += 1


# These are for the string views
__i = 0
SIC = __i; __i += 1
CANON_CASED = __i; __i += 1
NON_SPARSE = __i; __i += 1
SHAPE = __i; __i += 1
NR_STRING_VIEWS = __i


def get_string_views(unicode string, lexeme):
    views = ['' for _ in range(NR_STRING_VIEWS)]
    views[SIC] = string
    views[CANON_CASED] = canonicalize_case(string, lexeme)
    views[SHAPE] = get_string_shape(string)
    views[ASCIIFIED] = get_asciified(string)
    views[FIXED_VOCAB] = get_non_sparse(string, views[ASCIIFIED], views[CANON_CASED],
                                       views[SHAPE], lexeme)
    return views


def set_orth_flags(unicode string, flags_t flags)
    setters = [
        (ALPHA, is_alpha),
        (DIGIT, is_digit),
        (PUNCT, is_punct),
        (SPACE, is_space),
        (LOWER, is_lower),
        (UPPER, is_upper),
        (SPACE, is_space)
    ]

    for bit, setter in setters:
        if setter(string):
            flags |= 1 << bit
    return flags


cdef class German(spacy.Language):
    cdef Lexeme new_lexeme(self, unicode string, cluster=0, case_stats=None,
                           tag_freqs=None):
        return Lexeme(s, length, views, prob=prob, cluster=cluster,
                      flags=self.get_flags(string)
    
    cdef int find_split(self, unicode word):
        cdef size_t length = len(word)
        cdef int i = 0
        if word.startswith("'s") or word.startswith("'S"):
            return 2
        # Contractions
        if word.endswith("'s") and length >= 3:
            return length - 2
        # Leading punctuation
        if check_punct(word, 0, length):
            return 1
        elif length >= 1:
            # Split off all trailing punctuation characters
            i = 0
            while i < length and not check_punct(word, i, length):
                i += 1
        return i


DE = German('de')

lookup = DE.lookup
tokenize = DE.tokenize
load_clusters = DE.load_clusters
load_unigram_probs = DE.load_unigram_probs
load_case_stats = DE.load_case_stats
load_tag_stats = DE.load_tag_stats
