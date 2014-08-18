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
cimport cython


#cdef inline StringHash hash_string(unicode string, size_t length):
#    '''Hash unicode with MurmurHash64A'''
#    return hash(string)
#    #cdef bytes byte_string = string.encode('utf8')
#    #return mrmr.hash32(<char*>byte_string, len(byte_string) * sizeof(char), 0)


def get_normalized(unicode lex, size_t length):
    if lex.isalpha() and lex.islower():
        return lex
    else:
        return get_word_shape(lex, length)


def get_word_shape(unicode lex, length):
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
        self.chunks = dense_hash_map[StringHash, size_t]()
        self.vocab = dense_hash_map[StringHash, size_t]()
        self.chunks.set_empty_key(0)
        self.vocab.set_empty_key(0)
        self.load_tokenization(util.read_tokenization(name))

    cdef Tokens tokenize(self, unicode characters):
        cdef size_t i = 0
        cdef size_t start = 0
        cdef Lexeme** chunk
        cdef Tokens tokens = Tokens(self)
        for chunk_str in characters.split():
            chunk = self.lookup_chunk(chunk_str)
            i = 0
            while chunk[i] != NULL:
                tokens.append(<Lexeme_addr>chunk[i])
                i += 1
        return tokens

    cdef Lexeme* lookup(self, unicode string) except NULL:
        if len(string) == 0:
            return &BLANK_WORD
        cdef Lexeme* word = <Lexeme*>self.vocab[hash(string)]
        if word == NULL:
            word = self.new_lexeme(string)
        return word

    cdef Lexeme** lookup_chunk(self, unicode string) except NULL:
        assert len(string) != 0
        cdef Lexeme** chunk = <Lexeme**>self.chunks[hash(string)]
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
        word.lex = hash(string)
        self.bacov[word.lex] = string
        word.orth = self.new_orth(string)
        word.dist = self.new_dist(string)
        self.vocab[word.lex] = <size_t>word
        return word

    cdef Orthography* new_orth(self, unicode lex) except NULL:
        cdef unicode last3
        cdef unicode norm
        cdef unicode shape
        cdef int length 

        length = len(lex)
        orth = <Orthography*>calloc(1, sizeof(Orthography))
        orth.first = lex[0]
            
        orth.length = length
        orth.flags = set_orth_flags(lex, orth.length)
        orth.norm = hash(lex)
        last3 = substr(lex, length - 3, length, length)
        orth.last3 = hash(last3)
        norm = get_normalized(lex, length)
        orth.norm = hash(norm)
        shape = get_word_shape(lex, length)
        orth.shape = hash(shape)

        self.bacov[orth.last3] = last3
        self.bacov[orth.norm] = norm
        self.bacov[orth.shape] = shape

        return orth

    cdef Distribution* new_dist(self, unicode lex) except NULL:
        dist = <Distribution*>calloc(1, sizeof(Distribution))
        return dist

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
                self.new_lexeme(token_string)
