# cython: profile=True
# cython: embedsignature=True
'''Tokenize English text, using a scheme that differs from the Penn Treebank 3
scheme in several important respects:

* Whitespace added as tokens, except for single spaces. e.g.,

    >>> tokenize(u'\\nHello  \\tThere').strings
    [u'\\n', u'Hello', u' ', u'\\t', u'There']

* Contractions are normalized, e.g.

    >>> tokenize(u"isn't ain't won't he's").strings
    [u'is', u'not', u'are', u'not', u'will', u'not', u'he', u"__s"]
  
* Hyphenated words are split, with the hyphen preserved, e.g.:
    
    >>> tokenize(u'New York-based').strings
    [u'New', u'York', u'-', u'based']

* Full unicode support
* Email addresses, URLs, European-formatted dates and other numeric entities not
  found in the PTB are tokenized correctly
* Heuristic handling of word-final periods (PTB expects sentence boundary detection
  as a pre-process before tokenization.)

Take care to ensure you training and run-time data is tokenized according to the
same scheme. Tokenization problems are a major cause of poor performance for
NLP tools. If you're using a pre-trained model, the :py:mod:`spacy.ptb3` module
provides a fully Penn Treebank 3-compliant tokenizer.
'''
#The script translate_treebank_tokenization can be used to transform a treebank's
#annotation to use one of the spacy tokenization schemes.


from __future__ import unicode_literals

from libc.stdlib cimport malloc, calloc, free
from libc.stdint cimport uint64_t
from libcpp.vector cimport vector

cimport spacy


from spacy.orthography.latin cimport *
from spacy.lexeme cimport *

from .orthography.latin import *
from .lexeme import *



cdef class English(spacy.Language):
    # How to ensure the order here aligns with orthography.latin?
    view_funcs = [
        get_normalized,
        get_word_shape,
        get_last3
    ]

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

    cdef AttrType attr_of(self, LexID lex_id, AttrName attr) except *:
        cdef Lexeme* w = <Lexeme*>lex_id
        if attr == LEX:
            return <AttrType>w.lex
        elif attr == FIRST:
            return w.string[0]
        elif attr == LENGTH:
            return w.length
        elif attr == CLUSTER:
            return w.cluster
        elif attr == NORM:
            return w.string_views[0]
        elif attr == SHAPE:
            return w.string_views[1]
        elif attr == LAST3:
            return w.string_views[2]
        else:
            raise AttributeError(attr)




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

    The tokenization rules are defined in two places:

    * The data/en/tokenization table, which handles special cases like contractions;
    * The `spacy.en.English.find_split` function, which is used to split off punctuation etc.

    Args:
        string (unicode): The string to be tokenized. 

    Returns:
        tokens (Tokens): A Tokens object, giving access to a sequence of LexIDs.
    """
    return EN.tokenize(string)


cpdef LexID lookup(unicode string) except 0:
    """Retrieve (or create, if not found) a Lexeme ID for a string.

    The LexID is really a memory address, making dereferencing it essentially free.
    
    Args:
        string (unicode):  The string to be looked up. Must be unicode, not bytes.

    Returns:
        lexeme (LexID): A reference to a lexical type.
    """
    return <LexID>EN.lookup(string)


cpdef unicode unhash(StringHash hash_value):
    """Retrieve a string from a hash value. Mostly used for testing.

    In general you should avoid computing with strings, as they are slower than
    the intended ID-based usage. However, strings can be recovered if necessary,
    although no control is taken for hash collisions.

    Args:
        hash_value (StringHash): The hash of a string, returned by Python's hash()
        function.

    Returns:
        string (unicode): A unicode string that hashes to the hash_value.
    """
    return EN.unhash(hash_value)


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
