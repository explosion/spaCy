# cython: profile=True
# cython: embedsignature=True
'''Accessors for Lexeme properties, given a lex_id, which is cast to a Lexeme*.
Mostly useful from Python-space. From Cython-space, you can just cast to
Lexeme* yourself.
'''
from __future__ import unicode_literals

from libc.stdlib cimport malloc, calloc, free
from libc.stdint cimport uint64_t

from spacy.spacy cimport StringHash


cpdef int set_flags(LexID lex_id, object active_flags) except *:
    """Set orthographic bit flags for a Lexeme.

    Args:
        lex_id (LexemeID): A reference ID for a Lexeme.
        active_flags: A sequence of bits to set as True.
    """
    cdef size_t flag
    cdef Lexeme* w = <Lexeme*>lex_id
    for flag in active_flags:
        w.orth_flags |= 1 << flag


cpdef StringHash view_of(LexID lex_id, size_t view) except 0:
    return (<Lexeme*>lex_id).string_views[view]


cpdef StringHash lex_of(size_t lex_id) except 0:
    '''Access the `lex' field of the Lexeme pointed to by lex_id.

    The lex field is the hash of the string you would expect to get back from
    a standard tokenizer, i.e. the word with punctuation and other non-whitespace
    delimited tokens split off.  The other fields refer to properties of the
    string that the lex field stores a hash of, except sic and tail.

    >>> from spacy import en
    >>> [en.unhash(lex_of(lex_id) for lex_id in en.tokenize(u'Hi! world')]
    [u'Hi', u'!', u'world']
    '''
    return (<Lexeme*>lex_id).lex


cpdef ClusterID cluster_of(LexID lex_id) except 0:
    '''Access the `cluster' field of the Lexeme pointed to by lex_id, which
    gives an integer representation of the cluster ID of the word, 
    which should be understood as a binary address:

    >>> strings = (u'pineapple', u'apple', u'dapple', u'scalable')
    >>> token_ids = [lookup(s) for s in strings]
    >>> clusters = [cluster_of(t) for t in token_ids]
    >>> print ["{0:b"} % cluster_of(t) for t in token_ids]
    ["100111110110", "100111100100", "01010111011001", "100111110110"]

    The clusterings are unideal, but often slightly useful.
    "pineapple" and "apple" share a long prefix, indicating a similar meaning,
    while "dapple" is totally different. On the other hand, "scalable" receives
    the same cluster ID as "pineapple", which is not what we'd like.
    '''
    return (<Lexeme*>lex_id).cluster


cpdef char first_of(size_t lex_id) except 0:
    '''Access the `first' field of the Lexeme pointed to by lex_id, which
    stores the first character of the lex string of the word.

    >>> lex_id = lookup(u'Hello')
    >>> unhash(first_of(lex_id))
    u'H'
    '''
    return (<Lexeme*>lex_id).string[0]


cpdef size_t length_of(size_t lex_id) except 0:
    '''Access the `length' field of the Lexeme pointed to by lex_id, which stores
    the length of the string hashed by lex_of.'''
    cdef Lexeme* word = <Lexeme*>lex_id
    return word.length


cpdef double prob_of(size_t lex_id) except 0:
    '''Access the `prob' field of the Lexeme pointed to by lex_id, which stores
    the smoothed unigram log probability of the word, as estimated from a large
    text corpus.  By default, probabilities are based on counts from Gigaword,
    smoothed using Knesser-Ney; but any probabilities file can be supplied to
    load_probs.
    
    >>> prob_of(lookup(u'world'))
    -20.10340371976182
    '''
    return (<Lexeme*>lex_id).prob

DEF OFT_UPPER = 1
DEF OFT_TITLE = 2

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
    return (<Lexeme*>lex_id).dist_flags & (1 << OFT_UPPER)


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
    return (<Lexeme*>lex_id).dist_flags & (1 << OFT_TITLE)

cpdef bint check_orth_flag(size_t lex_id, OrthFlags flag) except *:
    return (<Lexeme*>lex_id).orth_flags & (1 << flag)


cpdef bint check_dist_flag(size_t lex_id, DistFlags flag) except *:
    return (<Lexeme*>lex_id).dist_flags & (1 << flag)


cpdef bint check_tag_flag(LexID lex_id, TagFlags flag) except *:
    return (<Lexeme*>lex_id).possible_tags & (1 << flag)
