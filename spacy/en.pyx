# cython: profile=True
'''Serve pointers to Lexeme structs, given strings. Maintain a reverse index,
so that strings can be retrieved from hashes.  Use 64-bit hash values and
boldly assume no collisions.
'''
from __future__ import unicode_literals

from libc.stdlib cimport malloc, calloc, free
from libc.stdint cimport uint64_t
from libcpp.vector cimport vector

from spacy.string_tools cimport substr

from . import util

cimport spacy


cdef class English(spacy.Language):
    cdef int find_split(self, unicode word, size_t length):
        cdef int i = 0
        # Contractions
        if word.endswith("'s"):
            return length - 2
        # Leading punctuation
        if is_punct(word, 0, length):
            return 1
        elif length >= 1:
            # Split off all trailing punctuation characters
            i = 0
            while i < length and not is_punct(word, i, length):
                i += 1
        return i


cdef bint is_punct(unicode word, size_t i, size_t length):
    # Don't count appostrophes as punct if the next char is a letter
    if word[i] == "'" and i < (length - 1) and word[i+1].isalpha():
        # ...Unless we're at 0
        return i == 0
    if word[i] == "-" and i < (length - 1) and word[i+1] == '-':
        return False
    # Don't count commas as punct if the next char is a number
    if word[i] == "," and i < (length - 1) and word[i+1].isdigit():
        return False
    # Don't count periods as punct if the next char is not whitespace
    if word[i] == "." and i < (length - 1) and not word[i+1].isspace():
        return False
    return not word[i].isalnum()


EN = English('en')


cpdef Tokens tokenize(unicode string):
    return EN.tokenize(string)
 

cpdef Lexeme_addr lookup(unicode string) except 0:
    return EN.lookup(-1, string, len(string))


cpdef unicode unhash(StringHash hash_value):
    return EN.unhash(hash_value)
