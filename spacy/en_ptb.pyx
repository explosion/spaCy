'''Serve pointers to Lexeme structs, given strings. Maintain a reverse index,
so that strings can be retrieved from hashes.  Use 64-bit hash values and
boldly assume no collisions.
'''
from __future__ import unicode_literals

from libc.stdlib cimport malloc, calloc, free
from libc.stdint cimport uint64_t
from libcpp.vector cimport vector

from spacy.lexeme cimport Lexeme
from spacy.string_tools cimport substr
from . import util

cimport spacy

BACOV = {}
VOCAB = Vocab()
VOCAB.set_empty_key(0)


spacy.load_tokenization(VOCAB, BACOV, util.read_tokenization('en_ptb'))


cpdef vector[Lexeme_addr] tokenize(unicode string) except *:
    return spacy.tokenize(VOCAB, BACOV, find_split, string)
 

cpdef Lexeme_addr lookup(unicode string) except 0:
    return spacy.lookup(VOCAB, BACOV, find_split, -1, string)


cpdef unicode unhash(StringHash hash_value):
    return spacy.unhash(BACOV, hash_value)


cdef vector[StringHash] make_string_views(unicode word):
    cdef unicode s
    return vector[StringHash]()
    #if word.isdigit() and len(word) == 4:
    #    return '!YEAR'
    #elif word[0].isdigit():
    #    return '!DIGITS'
    #else:
    #    return word.lower()
  

cdef int find_split(unicode word, size_t length):
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
    is_final = i == (length - 1)
    if word[i] == '.':
        return False
    if not is_final and word[i] == '-' and word[i+1] == '-':
        return True
    # Don't count appostrophes as punct if the next char is a letter
    if word[i] == "'" and i < (length - 1) and word[i+1].isalpha():
        return False
    punct_chars = set(',;:' + '@#$%&' + '!?' + '[({' + '})]')
    return word[i] in punct_chars
