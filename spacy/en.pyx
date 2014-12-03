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

cimport lang
from .typedefs cimport flags_t
import orth


cdef class English(Language):
    """English tokenizer, tightly coupled to lexicon.

    Attributes:
        name (unicode): The two letter code used by Wikipedia for the language.
        lexicon (Lexicon): The lexicon. Exposes the lookup method.
    """
    def set_flags(self, unicode string):
        cdef flags_t flags = 0
        flags |= orth.is_alpha(string) << IS_ALPHA
        flags |= orth.is_ascii(string) << IS_ASCII
        flags |= orth.is_digit(string) << IS_DIGIT
        flags |= orth.is_lower(string) << IS_LOWER
        flags |= orth.is_punct(string) << IS_PUNCT
        flags |= orth.is_space(string) << IS_SPACE
        flags |= orth.is_title(string) << IS_TITLE
        flags |= orth.is_upper(string) << IS_UPPER

        flags |= orth.like_url(string) << LIKE_URL
        flags |= orth.like_number(string) << LIKE_NUMBER
        return flags


EN = English('en')
