'''Serve pointers to Lexeme structs, given strings. Maintain a reverse index,
so that strings can be retrieved from hashes.  Use 64-bit hash values and
boldly assume no collisions.
'''
from __future__ import unicode_literals

from libc.stdlib cimport malloc, calloc, free
from libc.stdint cimport uint64_t

from spacy.lexeme cimport Lexeme
from ext.murmurhash cimport MurmurHash64A
from ext.murmurhash cimport MurmurHash64B
from . import util


STRINGS = {}
LEXEMES = dense_hash_map[StringHash, Lexeme_ptr]()
LEXEMES.set_empty_key(0)


cdef Lexeme BLANK_WORD = Lexeme(0, 0, 0, 0, 0, 0.0, 0, False, False, NULL)


def load_tokenization(token_rules):
    cdef Lexeme* word
    cdef StringHash hashed
    for chunk, lex, tokens in token_rules:
        hashed = hash_string(chunk, len(chunk))
        assert LEXEMES[hashed] == NULL
        word = _add(hashed, lex, len(lex), len(lex))
        for i, lex in enumerate(tokens):
            token_string = '%s:@:%d:@:%s' % (chunk, i, lex)
            length = len(token_string)
            hashed = hash_string(token_string, length)
            word.tail = _add(hashed, lex, 0, len(lex))
            word = word.tail


load_tokenization(util.read_tokenization('en'))

cpdef Lexeme_addr lookup(unicode string) except 0:
    '''.. function:: enumerate(sequence[, start=0])
    Fetch a Lexeme representing a word string. If the word has not been seen,
    construct one, splitting off any attached punctuation or clitics.  A
    reference to BLANK_WORD is returned for the empty string.
    
    To specify the boundaries of the word if it has not been seen, use lookup_chunk.
    '''
    if string == '':
        return <Lexeme_addr>&BLANK_WORD
    cdef size_t length = len(string)
    cdef StringHash hashed = hash_string(string, length)
    cdef Lexeme* word_ptr = LEXEMES[hashed]
    cdef size_t n
    if word_ptr == NULL:
        word_ptr = _add(hashed, string, _find_split(string, length), length)
    return <Lexeme_addr>word_ptr


cpdef Lexeme_addr lookup_chunk(unicode string, int start, int end) except 0:
    '''Fetch a Lexeme representing a word string. If the word has not been seen,
    construct one, given the specified start and end indices.  A negative index
    significes 0 for start, and the string length for end --- i.e. the string
    will not be sliced if start == -1 and end == -1.
    
    A reference to BLANK_WORD is returned for the empty string.
    '''
    if string == '':
        return <Lexeme_addr>&BLANK_WORD
    cdef size_t length = len(string)
    cdef StringHash hashed = hash_string(string, length)
    cdef Lexeme* chunk_ptr = LEXEMES[hashed]
    if chunk_ptr == NULL:
        chunk_ptr = _add(hashed, string, start, length)
    return <Lexeme_addr>chunk_ptr


cdef StringHash hash_string(unicode s, size_t length) except 0:
    '''Hash unicode with MurmurHash64A'''
    assert length
    return MurmurHash64A(<string_ptr>s, length * sizeof(Py_UNICODE), 0)


cpdef unicode unhash(StringHash hash_value):
    '''Fetch a string from the reverse index, given its hash value.'''
    cdef string_ptr string = STRINGS[hash_value]
    if string == NULL:
        raise ValueError(hash_value)

    return string


cdef unicode normalize_word_string(unicode word):
    '''Return a normalized version of the word, mapping:
    - 4 digit strings into !YEAR
    - Other digit strings into !DIGITS
    - All other strings into lower-case
    '''
    cdef unicode s
    if word.isdigit() and len(word) == 4:
        return '!YEAR'
    elif word[0].isdigit():
        return '!DIGITS'
    else:
        return word.lower()
    

cpdef unicode _substr(unicode string, int start, int end, size_t length):
    if end >= length:
        end = -1
    if start >= length:
        start = 0
    if start <= 0 and end < 0:
        return string
    elif start < 0:
        start = 0
    elif end < 0:
        end = length
    return string[start:end]
  

cdef Lexeme* _add(StringHash hashed, unicode string, int split, size_t length) except NULL:
    assert string
    assert split <= length
    word = _init_lexeme(string, hashed, split, length)
    LEXEMES[hashed] = word
    STRINGS[hashed] = string
    return word


cdef Lexeme* _init_lexeme(unicode string, StringHash hashed,
                          int split, size_t length) except NULL:
    assert split <= length
    cdef Lexeme* word = <Lexeme*>calloc(1, sizeof(Lexeme))

    word.first = <Py_UNICODE>(string[0] if string else 0)
    word.sic = hashed
    
    cdef unicode tail_string
    cdef unicode lex 
    if split != 0 and split < length:
        lex = _substr(string, 0, split, length)
        tail_string = _substr(string, split, length, length)
    else:
        lex = string
        tail_string = ''
    assert lex
    cdef unicode normed = normalize_word_string(lex)
    cdef unicode last3 = _substr(string, length - 3, length, length)

    assert normed
    assert len(normed)
    
    word.lex = hash_string(lex, len(lex))
    word.normed = hash_string(normed, len(normed))
    word.last3 = hash_string(last3, len(last3))

    STRINGS[word.lex] = lex
    STRINGS[word.normed] = normed
    STRINGS[word.last3] = last3

    # These are loaded later
    word.prob = 0
    word.cluster = 0
    word.oft_upper = False
    word.oft_title = False
    
    # Now recurse, and deal with the tail
    if tail_string:
        word.tail = <Lexeme*>lookup(tail_string)
    return word


cdef size_t _find_split(unicode word, size_t length):
    cdef int i = 0
    # Contractions
    if word.endswith("'s"):
        return length - 2
    # Leading punctuation
    if is_punct(word, 0, length):
        return 1
    elif length >= 1 and is_punct(word, length - 1, length):
        # Split off all trailing punctuation characters
        i = length - 1
        while i >= 2 and is_punct(word, i-1, length):
            i -= 1
    return i


cdef bint is_punct(unicode word, size_t i, size_t length):
    return not word[i].isalnum()
