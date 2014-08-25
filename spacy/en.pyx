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
#The script translate_treebank_tokenization can be used to transform a treebank's
#annotation to use one of the spacy tokenization schemes.


from __future__ import unicode_literals

from libc.stdlib cimport malloc, calloc, free
from libc.stdint cimport uint64_t

cimport spacy


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
    views[NON_SPARSE] = get_non_sparse(string, views[CANON_CASED], views[SHAPE],
                                       lexeme)
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




cdef class English(spacy.Language):
    cdef Lexeme new_lexeme(self, unicode string, cluster=0, prob=0, case_stats=None,
                           tag_freqs=None):
        return Lexeme(s, length, views, prob=prob, cluster=cluster,
                      flags=self.get_flags(string))

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


cpdef list tokenize(unicode string):
    """Tokenize a string.

    The tokenization rules are defined in two places:

    * The data/en/tokenization table, which handles special cases like contractions;
    * The :py:meth:`spacy.en.English.find_split` function, which is used to split off punctuation etc.

    Args:
        string (unicode): The string to be tokenized. 

    Returns:
        tokens (Tokens): A Tokens object, giving access to a sequence of LexIDs.
    """
    return EN.tokenize(string)


cpdef Lexeme lookup(unicode string):
    """Retrieve (or create, if not found) a Lexeme for a string, and return its ID.

    Properties of the Lexeme are accessed by passing LexID to the accessor methods.
    Access is cheap/free, as the LexID is the memory address of the Lexeme.
    
    Args:
        string (unicode):  The string to be looked up. Must be unicode, not bytes.

    Returns:
        lexeme (LexID): A reference to a lexical type.
    """
    return EN.lookup(string)


def add_string_views(view_funcs):
    """Add a string view to existing and previous lexical entries.

    Args:
        get_view (function): A unicode --> unicode function.

    Returns:
        view_id (int): An integer key you can use to access the view.
    """
    pass


def load_clusters(location):
    """Load cluster data.
    """
    pass


def load_unigram_probs(location):
    """Load unigram probabilities.
    """
    pass


def load_case_stats(location):
    """Load case stats.
    """
    pass


def load_tag_stats(location):
    """Load tag statistics.
    """
    pass
