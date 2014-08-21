# cython: embedsignature=True
from __future__ import unicode_literals

from spacy.lexeme cimport Lexeme

def get_normalized(unicode word):
    """Todo.

    Args:
        word (unicode)

    Returns:
        normalized (unicode)
    """
    if word.isalpha() and word.islower():
        return word
    else:
        return get_word_shape(word)


def get_word_shape(unicode word):
    """Todo.

    Args:
        word (unicode)

    Returns:
        shape (unicode)
    """
    cdef size_t length = len(word)
    shape = ""
    last = ""
    shape_char = ""
    seq = 0
    for c in word:
        if c.isalpha():
            if c.isupper():
                shape_char = "X"
            else:
                shape_char = "x"
        elif c.isdigit():
            shape_char = "d"
        else:
            shape_char = c
        if shape_char == last:
            seq += 1
        else:
            seq = 0
            last = shape_char
        if seq < 3:
            shape += shape_char
    assert shape
    return shape


cpdef unicode get_last3(unicode string):
    return string[-3:]


cpdef bint is_alpha(LexID lex_id) except *:
    """Check whether all characters in the word's string are alphabetic.
    
    Should match the :py:func:`unicode.isalpha()` function.

    >>> is_alpha(lookup(u'Hello'))
    True
    >>> is_alpha(lookup(u'العرب'))
    True
    >>> is_alpha(lookup(u'10'))
    False
    """
    return (<Lexeme*>lex_id).orth_flags & 1 << IS_ALPHA


cpdef bint is_digit(LexID lex_id) except *:
    """Check whether all characters in the word's string are numeric.
    
    Should match the :py:func:`unicode.isdigit()` function.

    >>> is_digit(lookup(u'10'))
    True
    >>> is_digit(lookup(u'๐'))
    True
    >>> is_digit(lookup(u'one'))
    False
    """
    return (<Lexeme*>lex_id).orth_flags & 1 << IS_DIGIT


cpdef bint is_punct(LexID lex_id) except *:
    """Check whether all characters belong to a punctuation unicode data category
    for a Lexeme ID.

    >>> is_punct(lookup(u'.'))
    True
    >>> is_punct(lookup(u'⁒'))
    True
    >>> is_punct(lookup(u' '))
    False
    """
    return (<Lexeme*>lex_id).orth_flags & 1 << IS_PUNCT


cpdef bint is_space(LexID lex_id) except *:
    """Give the result of unicode.isspace() for a Lexeme ID.

    >>> is_space(lookup(u'\\t'))
    True
    >>> is_space(lookup(u'<unicode space>'))
    True
    >>> is_space(lookup(u'Hi\\n'))
    False
    """
    return (<Lexeme*>lex_id).orth_flags & 1 << IS_SPACE


cpdef bint is_lower(LexID lex_id) except *:
    """Give the result of unicode.islower() for a Lexeme ID.

    >>> is_lower(lookup(u'hi'))
    True
    >>> is_lower(lookup(<unicode>))
    True
    >>> is_lower(lookup(u'10'))
    False
    """
    return (<Lexeme*>lex_id).orth_flags & 1 << IS_LOWER


cpdef bint is_upper(LexID lex_id) except *:
    """Give the result of unicode.isupper() for a Lexeme ID.

    >>> is_upper(lookup(u'HI'))
    True
    >>> is_upper(lookup(u'H10'))
    True
    >>> is_upper(lookup(u'10'))
    False
    """
    return (<Lexeme*>lex_id).orth_flags & 1 << IS_UPPER


cpdef bint is_title(LexID lex_id) except *:
    """Give the result of unicode.istitle() for a Lexeme ID.

    >>> is_title(lookup(u'Hi'))
    True
    >>> is_title(lookup(u'Hi1'))
    True
    >>> is_title(lookup(u'1'))
    False
    """
    return (<Lexeme*>lex_id).orth_flags & 1 << IS_TITLE


cpdef bint is_ascii(LexID lex_id) except *:
    """Give the result of checking whether all characters in the string are ascii.

    >>> is_ascii(lookup(u'Hi'))
    True
    >>> is_ascii(lookup(u' '))
    True
    >>> is_title(lookup(u'<unicode>'))
    False
    """
    return (<Lexeme*>lex_id).orth_flags & 1 << IS_ASCII


cpdef StringHash norm_of(LexID lex_id) except 0:
    """Return the hash of a "normalized" version of the string.

    Normalized strings are intended to be less sparse, while still capturing
    important lexical information.  See :py:func:`spacy.latin.orthography.normalize_string`
    for details of the normalization function.

    >>> unhash(norm_of(lookupu'Hi'))
    u'hi'
    >>> unhash(norm_of(lookup(u'255667')))
    u'shape=dddd'
    >>> unhash(norm_of(lookup(u'...')))
    u'...'
    """
    return (<Lexeme*>lex_id).string_views[NORM]


cpdef StringHash shape_of(LexID lex_id) except 0:
    """Return the hash of a string describing the word's "orthograpgic shape".

    Orthographic shapes are calculated by the :py:func:`spacy.orthography.latin.string_shape`
    function. Word shape features have been found useful for NER and POS tagging,
    e.g. Manning (2011)

    >>> unhash(shape_of(lookupu'Hi'))
    u'Xx'
    >>> unhash(shape_of(lookup(u'255667')))
    u'dddd'
    >>> unhash(shape_of(lookup(u'...')))
    u'...'
    """
    cdef Lexeme* w = <Lexeme*>lex_id
    return w.string_views[SHAPE]


cpdef StringHash last3_of(LexID lex_id) except 0:
    '''Return the hash of string[-3:], i.e. the last three characters of the word.

    >>> lex_ids = [lookup(w) for w in (u'Hello', u'!')]
    >>> [unhash(last3_of(lex_id)) for lex_id in lex_ids]
    [u'llo', u'!']
    '''
    return (<Lexeme*>lex_id).string_views[LAST3]
