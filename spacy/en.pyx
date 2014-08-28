# cython: profile=True
# cython: embedsignature=True
'''Tokenize English text, using a scheme that differs from the Penn Treebank 3
scheme in several important respects:

* Whitespace is added as tokens, except for single spaces. e.g.,

    >>> [w.string for w in tokenize(u'\\nHello  \\tThere')]
    [u'\\n', u'Hello', u' ', u'\\t', u'There']

* Contractions are normalized, e.g.

    >>> [w.string for w in u"isn't ain't won't he's")]
    [u'is', u'not', u'are', u'not', u'will', u'not', u'he', u"__s"]
  
* Hyphenated words are split, with the hyphen preserved, e.g.:
    
    >>> [w.string for w in tokenize(u'New York-based')]
    [u'New', u'York', u'-', u'based']

Other improvements:

* Full unicode support
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

from spacy import orth

TAG_THRESH = 0.5
UPPER_THRESH = 0.2
LOWER_THRESH = 0.5
TITLE_THRESH = 0.7

NR_FLAGS = 0

OFT_UPPER = NR_FLAGS; NR_FLAGS += 1
OFT_LOWER = NR_FLAGS; NR_FLAGS += 1
OFT_TITLE = NR_FLAGS; NR_FLAGS += 1

IS_ALPHA = NR_FLAGS; NR_FLAGS += 1
IS_DIGIT = NR_FLAGS; NR_FLAGS += 1
IS_PUNCT = NR_FLAGS; NR_FLAGS += 1
IS_SPACE = NR_FLAGS; NR_FLAGS += 1
IS_ASCII = NR_FLAGS; NR_FLAGS += 1
IS_TITLE = NR_FLAGS; NR_FLAGS += 1
IS_LOWER = NR_FLAGS; NR_FLAGS += 1
IS_UPPER = NR_FLAGS; NR_FLAGS += 1

CAN_PUNCT = NR_FLAGS; NR_FLAGS += 1
CAN_CONJ = NR_FLAGS; NR_FLAGS += 1
CAN_NUM = NR_FLAGS; NR_FLAGS += 1
CAN_DET = NR_FLAGS; NR_FLAGS += 1
CAN_ADP = NR_FLAGS; NR_FLAGS += 1
CAN_ADJ = NR_FLAGS; NR_FLAGS += 1
CAN_ADV = NR_FLAGS; NR_FLAGS += 1
CAN_VERB = NR_FLAGS; NR_FLAGS += 1
CAN_NOUN = NR_FLAGS; NR_FLAGS += 1
CAN_PDT = NR_FLAGS; NR_FLAGS += 1
CAN_POS = NR_FLAGS; NR_FLAGS += 1
CAN_PRON = NR_FLAGS; NR_FLAGS += 1
CAN_PRT = NR_FLAGS; NR_FLAGS += 1


cdef class English(Language):
    def __cinit__(self, name):
        flag_funcs = [0 for _ in range(NR_FLAGS)]
        
        flag_funcs[OFT_UPPER] = orth.oft_case('upper', UPPER_THRESH)
        flag_funcs[OFT_LOWER] = orth.oft_case('lower', LOWER_THRESH)
        flag_funcs[OFT_TITLE] = orth.oft_case('title', TITLE_THRESH)
        
        flag_funcs[IS_ALPHA] = orth.is_alpha
        flag_funcs[IS_DIGIT] = orth.is_digit
        flag_funcs[IS_PUNCT] = orth.is_punct
        flag_funcs[IS_SPACE] = orth.is_space
        flag_funcs[IS_TITLE] = orth.is_title
        flag_funcs[IS_LOWER] = orth.is_lower
        flag_funcs[IS_UPPER] = orth.is_upper
        
        flag_funcs[CAN_PUNCT] = orth.can_tag('PUNCT', TAG_THRESH)
        flag_funcs[CAN_CONJ] = orth.can_tag('CONJ', TAG_THRESH)
        flag_funcs[CAN_NUM] = orth.can_tag('NUM', TAG_THRESH)
        flag_funcs[CAN_DET] = orth.can_tag('DET', TAG_THRESH)
        flag_funcs[CAN_ADP] = orth.can_tag('ADP', TAG_THRESH)
        flag_funcs[CAN_ADJ] = orth.can_tag('ADJ', TAG_THRESH)
        flag_funcs[CAN_VERB] = orth.can_tag('VERB', TAG_THRESH)
        flag_funcs[CAN_NOUN] = orth.can_tag('NOUN', TAG_THRESH)
        flag_funcs[CAN_PDT] = orth.can_tag('PDT', TAG_THRESH)
        flag_funcs[CAN_POS] = orth.can_tag('POS', TAG_THRESH)
        flag_funcs[CAN_PRT] = orth.can_tag('PRT', TAG_THRESH)
        
        Language.__init__(self, name, flag_funcs)

    cpdef int _split_one(self, unicode word):
        cdef size_t length = len(word)
        cdef int i = 0
        if word.startswith("'s") or word.startswith("'S"):
            return 2
        # Contractions
        if word.endswith("'s") and length >= 3:
            return length - 2
        # Leading punctuation
        if _check_punct(word, 0, length):
            return 1
        elif length >= 1:
            # Split off all trailing punctuation characters
            i = 0
            while i < length and not _check_punct(word, i, length):
                i += 1
        return i

cdef bint _check_punct(unicode word, size_t i, size_t length):
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
