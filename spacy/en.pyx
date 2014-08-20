# cython: profile=True
# cython: embedsignature=True
'''Tokenize English text, allowing some differences from the Penn Treebank
tokenization, e.g. for email addresses, URLs, etc. Use en_ptb if full PTB
compatibility is the priority.
'''
from __future__ import unicode_literals

from libc.stdlib cimport malloc, calloc, free
from libc.stdint cimport uint64_t
from libcpp.vector cimport vector

cimport spacy


from spacy.orthography.latin cimport *



cdef class English(spacy.Language):
    cdef int set_orth(self, unicode word, Lexeme* lex) except -1:
        pass

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


cdef bint check_punct(unicode word, size_t i, size_t length):
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
    """Tokenize a string.

    Wraps EN.tokenize, where EN is an instance of the class English. The global
    variable manages the vocabulary, and memoizes tokenization rules.

    Args:
        string (unicode): The string to be split. Must be unicode, not bytes.

    Returns:
        tokens (Tokens): A Tokens instance, managing a vector of pointers to
        Lexeme structs. The Tokens instance supports sequence interfaces,
        but also offers a range of sequence-level operations, which are computed
        efficiently in Cython-space.
    """
    return EN.tokenize(string)
 

cpdef Lexeme_addr lookup(unicode string) except 0:
    """Retrieve (or create) a Lexeme for a string.

    Returns a Lexeme ID, which can be used via the accessor
    methods in spacy.lexeme

    Args:
        string (unicode):  The string to be looked up. Must be unicode, not bytes.

    Returns:
        LexemeID (size_t): An unsigned integer that allows the Lexeme to be retrieved.
        The LexemeID is really a memory address, making dereferencing it essentially
        free.
    """
    return <Lexeme_addr>EN.lookup(string)


cpdef unicode unhash(StringHash hash_value):
    """Retrieve a string from a hash value. Mostly used for testing.

    In general you should avoid computing with strings, as they are slower than
    the intended ID-based usage. However, strings can be recovered if necessary,
    although no control is taken for hash collisions.

    Args:
        hash_value (uint32_t): The hash of a string, returned by Python's hash()
        function.

    Returns:
        string (unicode): A unicode string that hashes to the hash_value.
    """
    return EN.unhash(hash_value)
