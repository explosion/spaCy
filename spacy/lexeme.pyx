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


cpdef StringHash lex_of(LexID lex_id) except 0:
    '''Access a hash of the word's string.

    >>> lex_of(lookup(u'Hi')) == hash(u'Hi')
    True
    '''
    return (<Lexeme*>lex_id).lex


cpdef ClusterID cluster_of(LexID lex_id) except 0:
    '''Access an integer representation of the word's Brown cluster.

    A Brown cluster is an address into a binary tree, which gives some (noisy)
    information about the word's distributional context.
    
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
    '''Access the first byte of a utf8 encoding of the word.

    >>> lex_id = lookup(u'Hello')
    >>> chr(first_of(lex_id))
    'H'
    '''
    return (<Lexeme*>lex_id).string[0]


cpdef size_t length_of(size_t lex_id) except 0:
    '''Access the (unicode) length of the word.
    '''
    cdef Lexeme* word = <Lexeme*>lex_id
    return word.length


cpdef double prob_of(size_t lex_id) except 0:
    '''Access an estimate of the word's unigram log probability.

    Probabilities are calculated from a large text corpus, and smoothed using
    simple Good-Turing.  Estimates are read from data/en/probabilities, and
    can be replaced using spacy.en.load_probabilities.
    
    >>> prob_of(lookup(u'world'))
    -20.10340371976182
    '''
    return (<Lexeme*>lex_id).prob

DEF OFT_UPPER = 1
DEF OFT_TITLE = 2

cpdef bint is_oft_upper(size_t lex_id):
    '''Check the OFT_UPPER distributional flag for the word.
    
    The OFT_UPPER flag records whether a lower-cased version of the word
    is found in all-upper case frequently in a large sample of text, where
    "frequently" is defined as P >= 0.95 (chosen for high mutual information for
    POS tagging).
    
    Case statistics are estimated from a large text corpus. Estimates are read
    from data/en/case_stats, and can be replaced using spacy.en.load_case_stats.
    
    >>> is_oft_upper(lookup(u'nato'))
    True
    >>> is_oft_upper(lookup(u'the')) 
    False
    '''
    return (<Lexeme*>lex_id).dist_flags & (1 << OFT_UPPER)


cpdef bint is_oft_title(size_t lex_id):
    '''Check the OFT_TITLE distributional flag for the word.
    
    The OFT_TITLE flag records whether a lower-cased version of the word
    is found title-cased (see string.istitle) frequently in a large sample of text,
    where "frequently" is defined as P >= 0.3 (chosen for high mutual information for
    POS tagging).
    
    Case statistics are estimated from a large text corpus. Estimates are read
    from data/en/case_stats, and can be replaced using spacy.en.load_case_stats.
    
    >>> is_oft_upper(lookup(u'john'))
    True
    >>> is_oft_upper(lookup(u'Bill')) 
    False
    '''
    return (<Lexeme*>lex_id).dist_flags & (1 << OFT_TITLE)

cpdef bint check_orth_flag(size_t lex_id, OrthFlags flag) except *:
    return (<Lexeme*>lex_id).orth_flags & (1 << flag)


cpdef bint check_dist_flag(size_t lex_id, DistFlags flag) except *:
    return (<Lexeme*>lex_id).dist_flags & (1 << flag)


cpdef bint check_tag_flag(LexID lex_id, TagFlags flag) except *:
    return (<Lexeme*>lex_id).possible_tags & (1 << flag)
