# cython: profile=True
from __future__ import unicode_literals

from libc.stdlib cimport calloc, free
from libcpp.pair cimport pair
from cython.operator cimport dereference as deref

from spacy.lexeme cimport Lexeme
from spacy.lexeme cimport BLANK_WORD

from spacy.string_tools cimport substr
from _hashing cimport WordTree
from _hashing cimport to_utf8

from . import util
from os import path
cimport cython


def get_normalized(unicode lex, size_t length):
    if lex.isalpha() and lex.islower():
        return lex
    else:
        return get_word_shape(lex, length)


def get_word_shape(lex, length):
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


def set_orth_flags(lex, length):
    return 0


cdef class Language:
    def __cinit__(self, name):
        self.name = name
        self.bacov = {}
        self.vocab = WordTree(0, 10)
        self.ortho = new Vocab()
        self.distri = new Vocab()
        self.distri[0].set_empty_key(0)
        self.ortho[0].set_empty_key(0)
        self.distri[0].set_deleted_key(1)
        self.ortho[0].set_deleted_key(1)
        self.load_tokenization(util.read_tokenization(name))

    property words:
        def __get__(self):
            return self.bacov.keys()

    def load_tokenization(self, token_rules=None):
        cdef Lexeme* word
        cdef StringHash hashed
        for chunk, lex, tokens in token_rules:
            word = self.init_lexeme(chunk)
            for i, lex in enumerate(tokens):
                token_string = '%s:@:%d:@:%s' % (chunk, i, lex)
                word.tail = self.init_lexeme(lex)
                word = word.tail

    def load_clusters(self):
        cdef Lexeme* w
        data_dir = path.join(path.dirname(__file__), '..', 'data', 'en')
        case_stats = util.load_case_stats(data_dir)
        brown_loc = path.join(data_dir, 'clusters')
        cdef size_t start 
        cdef int end 
        cdef unicode token_unicode
        cdef bytes token_bytes
        with util.utf8open(brown_loc) as browns_file:
            for i, line in enumerate(browns_file):
                cluster_str, token_unicode, freq_str = line.split()
                token_bytes = token_unicode.encode('utf8')
                # Decode as a little-endian string, so that we can do & 15 to get
                # the first 4 bits. See redshift._parse_features.pyx
                cluster = int(cluster_str[::-1], 2)
                upper_pc, title_pc = case_stats.get(token_string.lower(), (0.0, 0.0))
                word = self.init_lexeme(token_bytes)

    cpdef Tokens tokenize(self, unicode unicode_string):
        cdef bytes characters = unicode_string.encode('utf8')
        cdef size_t length = len(characters)
        
        cdef Tokens tokens = Tokens(self)
        cdef size_t start = 0

        cdef Lexeme* token
        cdef size_t i
        cdef unsigned char c

        for i in range(length):
            c = characters[i]
            if c == b' ':
                if start < i:
                    token = <Lexeme*>self.lookup(characters[start:i])
                    while token != NULL:
                        tokens.append(<Lexeme_addr>token)
                        token = token.tail
                start = i + 1
        if start < i:
            token = <Lexeme*>self.lookup(characters[start:])
            while token != NULL:
                tokens.append(<Lexeme_addr>token)
                token = token.tail
        return tokens

    cdef Lexeme_addr lookup(self, bytes string) except 0:
        '''Fetch a Lexeme representing a word string. If the word has not been seen,
        construct one, splitting off any attached punctuation or clitics.  A
        reference to BLANK_WORD is returned for the empty string.
        '''
        cdef size_t length = len(string)
        if length == 0:
            return <Lexeme_addr>&BLANK_WORD
        cdef Lexeme* word_ptr = <Lexeme*>self.vocab.get(string)
        if word_ptr == NULL:
            start = self.find_split(string, length)
            word_ptr = self.init_lexeme(string[)
            self.vocab.set(string[start:], <size_t>word_ptr)
        return <Lexeme_addr>word_ptr

    cdef Orthography* init_orth(self, StringHash hashed, unicode lex):
        cdef Orthography* orth = <Orthography*>calloc(1, sizeof(Orthography))
        orth.first = <Py_UNICODE>lex[0]

        cdef int length = len(lex)

        orth.length = length 
        orth.flags = set_orth_flags(lex, length)
        
        cdef unicode last3 = substr(lex, length - 3, length, length)
        cdef unicode norm = get_normalized(lex, length)
        cdef unicode shape = get_word_shape(lex, length)

        orth.last3 = self.hash_string(last3, len(last3))
        orth.shape = self.hash_string(shape, len(shape))
        orth.norm = self.hash_string(norm, len(norm))

        self.bacov[orth.last3] = last3.encode('utf8')
        self.bacov[orth.shape] = shape.encode('utf8')
        self.bacov[orth.norm] = norm.encode('utf8')

        self.ortho[0][hashed] = <size_t>orth
        return orth

    cdef unicode unhash(self, StringHash hash_value):
        '''Fetch a string from the reverse index, given its hash value.'''
        return self.bacov[hash_value].decode('utf8')

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
    while word != NULL:
        tokens.push_back(<size_t>word)
        word = word.tail
    return tokens
