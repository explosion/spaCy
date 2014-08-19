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
    cdef int find_split(self, unicode word):
        cdef size_t length = len(word)
        cdef int i = 0
        if word.startswith("'s") or word.startswith("'S"):
            return 2
        # Contractions
        if word.endswith("'s") and length >= 3:
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
    return <Lexeme_addr>EN.lookup(string)


cpdef unicode unhash(StringHash hash_value):
    return EN.unhash(hash_value)


cpdef bint is_oft_upper(size_t lex_id):
    '''Access the `oft_upper' field of the Lexeme pointed to by lex_id, which
    stores whether the lowered version of the string hashed by `lex' is found
    in all-upper case frequently in a large sample of text.  Users are free
    to load different data, by default we use a sample from Wikipedia, with
    a threshold of 0.95, picked to maximize mutual information for POS tagging.

    >>> is_oft_upper(lookup(u'abc'))
    True
    >>> is_oft_upper(lookup(u'aBc')) # This must get the same answer
    True
    '''
    return (<Lexeme*>lex_id).dist.flags & OFT_UPPER


cpdef bint is_oft_title(size_t lex_id):
    '''Access the `oft_upper' field of the Lexeme pointed to by lex_id, which
    stores whether the lowered version of the string hashed by `lex' is found
    title-cased frequently in a large sample of text.  Users are free
    to load different data, by default we use a sample from Wikipedia, with
    a threshold of 0.3, picked to maximize mutual information for POS tagging.

    >>> is_oft_title(lookup(u'marcus'))
    True
    >>> is_oft_title(lookup(u'MARCUS')) # This must get the same value
    True
    '''
    return (<Lexeme*>lex_id).dist.flags & OFT_TITLE
