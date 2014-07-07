# cython: profile=True
from __future__ import unicode_literals

from libc.stdlib cimport calloc, free

from ext.murmurhash cimport MurmurHash64A
from ext.murmurhash cimport MurmurHash64B

from spacy.lexeme cimport init_lexeme
from spacy.lexeme cimport BLANK_WORD

from spacy.string_tools cimport is_whitespace

from . import util
from os import path
cimport cython


cdef class Language:
    def __cinit__(self, name):
        self.name = name
        self.bacov = {}
        self.vocab = new Vocab()
        self.vocab[0].set_empty_key(0)
        self.load_tokenization(util.read_tokenization(name))

    def load_tokenization(self, token_rules=None):
        cdef Lexeme* word
        cdef StringHash hashed
        for chunk, lex, tokens in token_rules:
            hashed = self.hash_string(chunk, len(chunk))
            word = self._add(hashed, lex, len(lex), len(lex))
            for i, lex in enumerate(tokens):
                token_string = '%s:@:%d:@:%s' % (chunk, i, lex)
                length = len(token_string)
                hashed = self.hash_string(token_string, length)
                word.tail = self._add(hashed, lex, 0, len(lex))
                word = word.tail

    def load_clusters(self):
        cdef Lexeme* w
        data_dir = path.join(path.dirname(__file__), '..', 'data', 'en')
        case_stats = util.load_case_stats(data_dir)
        brown_loc = path.join(data_dir, 'clusters')
        cdef size_t start 
        cdef int end 
        with util.utf8open(brown_loc) as browns_file:
            for i, line in enumerate(browns_file):
                cluster_str, token_string, freq_str = line.split()
                # Decode as a little-endian string, so that we can do & 15 to get
                # the first 4 bits. See redshift._parse_features.pyx
                cluster = int(cluster_str[::-1], 2)
                upper_pc, title_pc = case_stats.get(token_string.lower(), (0.0, 0.0))
                hashed = self.hash_string(token_string, len(token_string))
                word = self._add(hashed, token_string,
                                len(token_string), len(token_string))
   
    cdef StringHash hash_string(self, Py_UNICODE* s, size_t length) except 0:
        '''Hash unicode with MurmurHash64A'''
        return MurmurHash64A(<Py_UNICODE*>s, length * sizeof(Py_UNICODE), 0)

    cdef unicode unhash(self, StringHash hash_value):
        '''Fetch a string from the reverse index, given its hash value.'''
        return self.bacov[hash_value]

    cdef Lexeme_addr lookup(self, int start, Py_UNICODE* string, size_t length) except 0:
        '''Fetch a Lexeme representing a word string. If the word has not been seen,
        construct one, splitting off any attached punctuation or clitics.  A
        reference to BLANK_WORD is returned for the empty string.
    
        To specify the boundaries of the word if it has not been seen, use lookup_chunk.
        '''
        if length == 0:
            return <Lexeme_addr>&BLANK_WORD
        cdef StringHash hashed = self.hash_string(string, length)
        cdef Lexeme* word_ptr = <Lexeme*>self.vocab[0][hashed]
        if word_ptr == NULL:
            start = self.find_split(string, length) if start == -1 else start
            word_ptr = self._add(hashed, string, start, length)
        return <Lexeme_addr>word_ptr

    cdef Lexeme* _add(self, StringHash hashed, unicode string, int split, size_t length):
        word = init_lexeme(self, string, hashed, split, length)
        self.vocab[0][hashed] = <Lexeme_addr>word
        self.bacov[hashed] = string
        return word   

    cpdef Tokens tokenize(self, unicode string):
        cdef size_t length = len(string)
        cdef Py_UNICODE* characters = <Py_UNICODE*>string

        cdef size_t i
        cdef Py_UNICODE c

        cdef Tokens tokens = Tokens(self)
        cdef Py_UNICODE* current = <Py_UNICODE*>calloc(len(string), sizeof(Py_UNICODE))
        cdef size_t word_len = 0
        cdef Lexeme* token
        for i in range(length):
            c = characters[i]
            if _is_whitespace(c):
                if word_len != 0:
                    token = <Lexeme*>self.lookup(-1, current, word_len)
                    while token != NULL:
                        tokens.append(<Lexeme_addr>token)
                        token = token.tail
                        for j in range(word_len+1):
                            current[j] = 0
                    word_len = 0
            else:
                current[word_len] = c
                word_len += 1
        if word_len != 0:
            token = <Lexeme*>self.lookup(-1, current, word_len)
            while token != NULL:
                tokens.append(<Lexeme_addr>token)
                token = token.tail
        free(current)
        return tokens

    cdef int find_split(self, unicode word, size_t length):
        return -1



cdef inline bint _is_whitespace(Py_UNICODE c) nogil:
    if c == ' ':
        return True
    elif c == '\n':
        return True
    elif c == '\t':
        return True
    else:
        return False


cpdef vector[size_t] expand_chunk(size_t addr) except *:
    cdef vector[size_t] tokens = vector[size_t]()
    word = <Lexeme*>addr
    while word is not NULL:
        tokens.push_back(<size_t>word)
        word = word.tail
    return tokens
