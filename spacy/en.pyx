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


cdef class English(Language):
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


# Thresholds for frequency related flags
TAG_THRESH = 0.5
LOWER_THRESH = 0.5
UPPER_THRESH = 0.3
TITLE_THRESH = 0.9


# Python-readable flag constants --- can't read an enum from Python
ALPHA = EN.lexicon.add_flag(orth.is_alpha)
DIGIT = EN.lexicon.add_flag(orth.is_digit)
PUNCT = EN.lexicon.add_flag(orth.is_punct)
SPACE = EN.lexicon.add_flag(orth.is_space)
PUNCT = EN.lexicon.add_flag(orth.is_punct)
ASCII = EN.lexicon.add_flag(orth.is_ascii)
TITLE = EN.lexicon.add_flag(orth.is_title)
LOWER = EN.lexicon.add_flag(orth.is_lower)
UPPER = EN.lexicon.add_flag(orth.is_upper)

OFT_LOWER = EN.lexicon.add_flag(orth.case_trend('lower', LOWER_THRESH))
OFT_UPPER = EN.lexicon.add_flag(orth.case_trend('upper', UPPER_THRESH))
OFT_TITLE = EN.lexicon.add_flag(orth.case_trend('title', TITLE_THRESH))

CAN_PUNCT = EN.lexicon.add_flag(orth.can_tag("PUNCT", TAG_THRESH))
CAN_CONJ = EN.lexicon.add_flag(orth.can_tag("CONJ", TAG_THRESH))
CAN_NUM = EN.lexicon.add_flag(orth.can_tag("NUM", TAG_THRESH))
CAN_N = EN.lexicon.add_flag(orth.can_tag("N", TAG_THRESH))
CAN_DET = EN.lexicon.add_flag(orth.can_tag("DET", TAG_THRESH))
CAN_ADP = EN.lexicon.add_flag(orth.can_tag("ADP", TAG_THRESH))
CAN_ADJ = EN.lexicon.add_flag(orth.can_tag("ADJ", TAG_THRESH))
CAN_ADV = EN.lexicon.add_flag(orth.can_tag("ADV", TAG_THRESH))
CAN_VERB = EN.lexicon.add_flag(orth.can_tag("VERB", TAG_THRESH))
CAN_NOUN = EN.lexicon.add_flag(orth.can_tag("NOUN", TAG_THRESH))
CAN_PDT = EN.lexicon.add_flag(orth.can_tag("PDT", TAG_THRESH))
CAN_POS = EN.lexicon.add_flag(orth.can_tag("POS", TAG_THRESH))
CAN_PRON = EN.lexicon.add_flag(orth.can_tag("PRON", TAG_THRESH))
CAN_PRT = EN.lexicon.add_flag(orth.can_tag("PRT", TAG_THRESH))


# These are the name of string transforms
SIC = EN.lexicon.add_transform(orth.sic_string)
CANON_CASED = EN.lexicon.add_transform(orth.canon_case)
SHAPE = EN.lexicon.add_transform(orth.word_shape)
NON_SPARSE = EN.lexicon.add_transform(orth.non_sparse)
