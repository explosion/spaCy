# cython: profile=True
'''Accessors for Lexeme properties, given a lex_id, which is cast to a Lexeme*.
Mostly useful from Python-space. From Cython-space, you can just cast to
Lexeme* yourself.
'''
from __future__ import unicode_literals

from spacy.string_tools cimport substr

from libc.stdlib cimport malloc, calloc, free
from libc.stdint cimport uint64_t
from libcpp.vector cimport vector

from spacy.spacy cimport StringHash


cpdef StringHash attr_of(size_t lex_id, StringAttr attr) except 0:
    if attr == LEX:
        return lex_of(lex_id)
    elif attr == NORM:
        return norm_of(lex_id)
    elif attr == SHAPE:
        return shape_of(lex_id)
    elif attr == LAST3:
        return last3_of(lex_id)
    elif attr == LENGTH:
        return length_of(lex_id)
    else:
        raise StandardError


cpdef StringHash lex_of(size_t lex_id) except 0:
    '''Access the `lex' field of the Lexeme pointed to by lex_id.

    The lex field is the hash of the string you would expect to get back from
    a standard tokenizer, i.e. the word with punctuation and other non-whitespace
    delimited tokens split off.  The other fields refer to properties of the
    string that the lex field stores a hash of, except sic and tail.

    >>> [unhash(lex_of(lex_id) for lex_id in from_string(u'Hi! world')]
    [u'Hi', u'!', u'world']
    '''
    return (<Lexeme*>lex_id).lex


cpdef StringHash norm_of(size_t lex_id) except 0:
    '''Access the `lex' field of the Lexeme pointed to by lex_id.

    The lex field is the hash of the string you would expect to get back from
    a standard tokenizer, i.e. the word with punctuation and other non-whitespace
    delimited tokens split off.  The other fields refer to properties of the
    string that the lex field stores a hash of, except sic and tail.

    >>> [unhash(lex_of(lex_id) for lex_id in from_string(u'Hi! world')]
    [u'Hi', u'!', u'world']
    '''
    return (<Lexeme*>lex_id).orth.norm


cpdef StringHash shape_of(size_t lex_id) except 0:
    return (<Lexeme*>lex_id).orth.shape


cpdef StringHash last3_of(size_t lex_id) except 0:
    '''Access the `last3' field of the Lexeme pointed to by lex_id, which stores
    the hash of the last three characters of the word:

    >>> lex_ids = [lookup(w) for w in (u'Hello', u'!')]
    >>> [unhash(last3_of(lex_id)) for lex_id in lex_ids]
    [u'llo', u'!']
    '''
    return (<Lexeme*>lex_id).orth.last3


cpdef ClusterID cluster_of(size_t lex_id) except 0:
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
    return (<Lexeme*>lex_id).dist.cluster


cpdef Py_UNICODE first_of(size_t lex_id):
    '''Access the `first' field of the Lexeme pointed to by lex_id, which
    stores the first character of the lex string of the word.

    >>> lex_id = lookup(u'Hello')
    >>> unhash(first_of(lex_id))
    u'H'
    '''
    return (<Lexeme*>lex_id).orth.first


cpdef size_t length_of(size_t lex_id) except *:
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
    return (<Lexeme*>lex_id).dist.prob


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
    return (<Lexeme*>lex_id).dist.flags & OFT_UPPER


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
    return (<Lexeme*>lex_id).dist.flags & OFT_TITLE

cpdef bint check_orth_flag(size_t lex_id, OrthFlag flag) except *:
    return (<Lexeme*>lex_id).orth.flags & (1 << flag)


cpdef bint check_dist_flag(size_t lex_id, DistFlag flag) except *:
    return (<Lexeme*>lex_id).dist.flags & (1 << flag)
