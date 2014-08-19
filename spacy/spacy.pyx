# cython: profile=True
from __future__ import unicode_literals

from libc.stdlib cimport calloc, free
from libcpp.pair cimport pair
from cython.operator cimport dereference as deref

from spacy.lexeme cimport Lexeme
from spacy.lexeme cimport BLANK_WORD

from spacy.string_tools cimport substr

from . import util
from os import path

DIST_FLAGS = {}
TAGS = {}


def get_normalized(unicode lex):
    if lex.isalpha() and lex.islower():
        return lex
    else:
        return get_word_shape(lex)


def get_word_shape(unicode lex):
    cdef size_t length = len(lex)
    shape = ""
    last = ""
    shape_char = ""
    seq = 0
    for c in lex:
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


def set_orth_flags(lex):
    return 0


cdef class Language:
    def __cinit__(self, name):
        self.name = name
        self.bacov = {}
        self.chunks = dense_hash_map[StringHash, size_t]()
        self.vocab = dense_hash_map[StringHash, size_t]()
        self.chunks.set_empty_key(0)
        self.vocab.set_empty_key(0)
        self.load_tokenization(util.read_tokenization(name))
        #self.load_dist_info(util.read_dist_info(name))

    cdef Tokens tokenize(self, unicode string):
        cdef Lexeme** chunk
        cdef Tokens tokens = Tokens(self)
        cdef size_t length = len(string)
        cdef size_t start = 0
        cdef size_t i = 0
        for c in string:
            if _is_whitespace(c):
                if start < i:
                    chunk = self.lookup_chunk(string[start:i])
                    _extend(tokens, chunk)
                start = i + 1
            i += 1
        if start < i:
            chunk = self.lookup_chunk(string[start:])
            _extend(tokens, chunk)
        return tokens

    cdef Lexeme* lookup(self, unicode string) except NULL:
        if len(string) == 0:
            return &BLANK_WORD
        cdef Lexeme* word = <Lexeme*>self.vocab[hash(string)]
        if word == NULL:
            word = self.new_lexeme(string)
        return word

    cdef Lexeme** lookup_chunk(self, unicode string) except NULL:
        cdef StringHash h = hash(string)
        cdef Lexeme** chunk = <Lexeme**>self.chunks[h]
        cdef int split
        if chunk == NULL:
            chunk = self.new_chunk(string, self.find_substrings(string))
        return chunk

    cdef Lexeme** new_chunk(self, unicode string, list substrings) except NULL:
        cdef Lexeme** chunk = <Lexeme**>calloc(len(substrings) + 1, sizeof(Lexeme*))
        for i, substring in enumerate(substrings):
            chunk[i] = self.lookup(substring)
        chunk[i + 1] = NULL
        self.chunks[hash(string)] = <size_t>chunk
        return chunk

    cdef Lexeme* new_lexeme(self, unicode string) except NULL:
        cdef Lexeme* word = <Lexeme*>calloc(1, sizeof(Lexeme))
        cdef bytes byte_string = string.encode('utf8')
        word.string = <char*>byte_string
        word.length = len(byte_string)
        word.orth.flags = set_orth_flags(string)
        cdef unicode norm = get_normalized(string)
        cdef unicode shape = get_word_shape(string)
        cdef unicode last3 = string[-3:]
        word.lex = hash(string)
        word.orth.norm = hash(norm)
        word.orth.shape = hash(shape)
        word.orth.last3 = hash(last3)
        self.bacov[word.lex] = string
        self.bacov[word.orth.norm] = norm
        self.bacov[word.orth.shape] = shape
        self.bacov[word.orth.last3] = last3

        self.vocab[hash(string)] = <size_t>word
        return word

    cdef unicode unhash(self, StringHash hash_value):
        '''Fetch a string from the reverse index, given its hash value.'''
        return self.bacov[hash_value]

    cpdef list find_substrings(self, unicode word):
        substrings = []
        while word:
            split = self.find_split(word)
            if split == 0:
                substrings.append(word)
                break
            substrings.append(word[:split])
            word = word[split:]
        return substrings

    cdef int find_split(self, unicode word):
        return len(word)

    def load_tokenization(self, token_rules=None):
        for chunk, tokens in token_rules:
            self.new_chunk(chunk, tokens)

    def load_dist_info(self, dist_info):
        cdef unicode string
        cdef dict word_dist
        cdef Lexeme* w
        for string, word_dist in dist_info.items():
            w = self.lookup(string)
            w.dist.prob = word_dist.prob
            w.dist.cluster = word_dist.cluster
            for flag in word_dist.flags:
                w.dist.flags |= DIST_FLAGS[flag]
            for tag in word_dist.tagdict:
                w.dist.tagdict |= TAGS[tag]


cdef inline bint _is_whitespace(Py_UNICODE c) nogil:
    if c == ' ':
        return True
    elif c == '\n':
        return True
    elif c == '\t':
        return True
    else:
        return False


cdef inline int _extend(Tokens tokens, Lexeme** chunk) nogil:
    cdef size_t i = 0
    while chunk[i] != NULL:
        tokens.vctr[0].push_back(<Lexeme_addr>chunk[i])
        tokens.length += 1
        i += 1
