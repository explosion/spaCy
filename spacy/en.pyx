# cython: profile=True
# cython: embedsignature=True
'''Tokenize English text, using a scheme that differs from the Penn Treebank 3
scheme in several important respects:

* Whitespace is added as tokens, except for single spaces. e.g.,

    >>> [w.string for w in EN.tokenize(u'\\nHello  \\tThere')]
    [u'\\n', u'Hello', u' ', u'\\t', u'There']

* Contractions are normalized, e.g.

    >>> [w.string for w in EN.tokenize(u"isn't ain't won't he's")]
    [u'is', u'not', u'are', u'not', u'will', u'not', u'he', u"__s"]
  
* Hyphenated words are split, with the hyphen preserved, e.g.:
    
    >>> [w.string for w in EN.tokenize(u'New York-based')]
    [u'New', u'York', u'-', u'based']

Other improvements:

* Email addresses, URLs, European-formatted dates and other numeric entities not
  found in the PTB are tokenized correctly
* Heuristic handling of word-final periods (PTB expects sentence boundary detection
  as a pre-process before tokenization.)

Take care to ensure your training and run-time data is tokenized according to the
same scheme. Tokenization problems are a major cause of poor performance for
NLP tools. If you're using a pre-trained model, the :py:mod:`spacy.ptb3` module
provides a fully Penn Treebank 3-compliant tokenizer.
'''
# TODO
#The script translate_treebank_tokenization can be used to transform a treebank's
#annotation to use one of the spacy tokenization schemes.


from __future__ import unicode_literals

from libc.stdlib cimport malloc, calloc, free
from libc.stdint cimport uint64_t

cimport lang
from spacy.lexeme cimport lexeme_check_flag
from spacy.lexeme cimport lexeme_string_view
from spacy._hashing cimport PointerHash


from spacy import orth


cdef class English(Language):
    """English tokenizer, tightly coupled to lexicon.

    Attributes:
        name (unicode): The two letter code used by Wikipedia for the language.
        lexicon (Lexicon): The lexicon. Exposes the lookup method.
    """
    cdef int _find_prefix(self, Py_UNICODE* chars, size_t length) except -1:
        cdef Py_UNICODE c0 = chars[0]
        cdef Py_UNICODE c1 = chars[1]
        if c0 == ",":
            return 1
        elif c0 == '"':
            return 1
        elif c0 == "(":
            return 1
        elif c0 == "[":
            return 1
        elif c0 == "{":
            return 1
        elif c0 == "*":
            return 1
        elif c0 == "<":
            return 1
        elif c0 == "$":
            return 1
        elif c0 == "£":
            return 1
        elif c0 == "€":
            return 1
        elif c0 == "\u201c":
            return 1
        elif c0 == "'":
            if c1 == "s":
                return 2
            elif c1 == "S":
                return 2
            elif c1 == "'":
                return 2
            else:
                return 1
        elif c0 == "`":
            if c1 == "`":
                return 2
            else:
                return 1
        else:
            return 0
        
abbreviations = set(['U.S', 'u.s', 'U.N', 'Ms', 'Mr', 'P'])
cdef bint _check_punct(Py_UNICODE* characters, size_t i, size_t length):
    cdef unicode char_i = characters[i]
    cdef unicode char_i1 = characters[i+1]
    # Don't count appostrophes as punct if the next char is a letter
    if characters[i] == "'" and i < (length - 1) and char_i1.isalpha():
        return i == 0
    if characters[i] == "-":
        return False
        #and i < (length - 1) and characters[i+1] == '-':
        #return False
    # Don't count commas as punct if the next char is a number
    if characters[i] == "," and i < (length - 1) and char_i1.isdigit():
        return False
    if characters[i] == "." and i < (length - 1):
        return False
    if characters[i] == "." and characters[:i] in abbreviations:
        return False
    return not char_i.isalnum()


EN = English('en', [], [])
