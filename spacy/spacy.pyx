from __future__ import unicode_literals

from ext.murmurhash cimport MurmurHash64A
from ext.murmurhash cimport MurmurHash64B

from spacy.lexeme cimport init_lexeme
from spacy.lexeme cimport BLANK_WORD

from spacy.string_tools cimport is_whitespace

from . import util


cdef load_tokenization(Vocab& vocab, dict bacov, token_rules):
    cdef Lexeme* word
    cdef StringHash hashed
    for chunk, lex, tokens in token_rules:
        hashed = hash_string(chunk, len(chunk))
        assert vocab[hashed] == 0
        word = _add(vocab, bacov, <Splitter>NULL, hashed, lex, len(lex), len(lex))
        for i, lex in enumerate(tokens):
            token_string = '%s:@:%d:@:%s' % (chunk, i, lex)
            length = len(token_string)
            hashed = hash_string(token_string, length)
            word.tail = _add(vocab, bacov, <Splitter>NULL, hashed, lex, 0, len(lex))
            word = word.tail


cdef vector[Lexeme_addr] tokenize(Vocab& vocab, dict bacov, Splitter splitter,
                                  unicode string) except *:
    cdef size_t length = len(string)
    cdef Py_UNICODE* characters = <Py_UNICODE*>string

    cdef size_t i
    cdef Py_UNICODE c

    cdef vector[Lexeme_addr] tokens = vector[Lexeme_addr]()
    cdef unicode current = u''
    cdef Lexeme* token
    for i in range(length):
        c = characters[i]
        if is_whitespace(c):
            if current:
                token = <Lexeme*>lookup(vocab, bacov, splitter, -1, current)
                while token != NULL:
                    tokens.push_back(<Lexeme_addr>token)
                    token = token.tail
            current = u''
        else:
            current += c
    if current:
        token = <Lexeme*>lookup(vocab, bacov, splitter, -1, current)
        while token != NULL:
            tokens.push_back(<Lexeme_addr>token)
            token = token.tail
    return tokens


cdef Lexeme_addr lookup(Vocab& vocab, dict bacov, Splitter find_split, int start,
                        unicode string) except 0:
    '''Fetch a Lexeme representing a word string. If the word has not been seen,
    construct one, splitting off any attached punctuation or clitics.  A
    reference to BLANK_WORD is returned for the empty string.
    
    To specify the boundaries of the word if it has not been seen, use lookup_chunk.
    '''
    if string == '':
        return <Lexeme_addr>&BLANK_WORD
    cdef size_t length = len(string)
    cdef StringHash hashed = hash_string(string, length)
    cdef Lexeme* word_ptr = <Lexeme*>vocab[hashed]
    if word_ptr == NULL:
        start = find_split(string, length) if start == -1 else start
        word_ptr = _add(vocab, bacov, find_split, hashed, string, start, length)
    return <Lexeme_addr>word_ptr


cpdef vector[size_t] expand_chunk(size_t addr) except *:
    cdef vector[size_t] tokens = vector[size_t]()
    word = <Lexeme*>addr
    while word is not NULL:
        tokens.push_back(<size_t>word)
        word = word.tail
    return tokens


cdef StringHash hash_string(unicode s, size_t length) except 0:
    '''Hash unicode with MurmurHash64A'''
    assert length
    return MurmurHash64A(<Py_UNICODE*>s, length * sizeof(Py_UNICODE), 0)


cdef unicode unhash(dict bacov, StringHash hash_value):
    '''Fetch a string from the reverse index, given its hash value.'''
    return bacov[hash_value]


cdef Lexeme* _add(Vocab& vocab, dict bacov, Splitter find_split, StringHash hashed,
                  unicode string, int split, size_t length) except NULL:
    assert string
    assert split <= length
    word = init_lexeme(vocab, bacov, find_split, string, hashed, split, length)
    vocab[hashed] = <Lexeme_addr>word
    bacov[hashed] = string
    return word
