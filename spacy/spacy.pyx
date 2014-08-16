# cython: profile=True
from __future__ import unicode_literals

from libc.stdlib cimport calloc, free
from libcpp.pair cimport pair
from cython.operator cimport dereference as deref

from murmurhash cimport mrmr
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
        self.vocab = WordTree(0, 5)
        self.ortho = new Vocab()
        self.distri = new Vocab()
        self.distri[0].set_empty_key(0)
        self.ortho[0].set_empty_key(0)
        self.load_tokenization(util.read_tokenization(name))

    cpdef Tokens tokenize(self, unicode characters):
        cdef size_t i = 0
        cdef size_t start = 0

        cdef Tokens tokens = Tokens(self)
        cdef Lexeme* token
        for c in characters:
            if _is_whitespace(c):
                if start < i:
                    token = <Lexeme*>self.lookup_chunk(characters[start:i])
                    while token != NULL:
                        tokens.append(<Lexeme_addr>token)
                        token = token.tail
                start = i + 1
            i += 1
        if start < i:
            token = <Lexeme*>self.lookup_chunk(characters[start:])
            while token != NULL:
                tokens.append(<Lexeme_addr>token)
                token = token.tail
        return tokens

    cdef Lexeme_addr lookup(self, unicode string) except 0:
        cdef size_t length = len(string)
        if length == 0:
            return <Lexeme_addr>&BLANK_WORD

        cdef StringHash hashed = hash(string)
        # First, check words seen 2+ times
        cdef Lexeme* word_ptr = <Lexeme*>self.vocab.get(string)
        if word_ptr == NULL:
            word_ptr = self.new_lexeme(string, string)
        return <Lexeme_addr>word_ptr

    cdef Lexeme_addr lookup_chunk(self, unicode string) except 0:
        '''Fetch a Lexeme representing a word string. If the word has not been seen,
        construct one, splitting off any attached punctuation or clitics.  A
        reference to BLANK_WORD is returned for the empty string.
        '''
        cdef size_t length = len(string)
        if length == 0:
            return <Lexeme_addr>&BLANK_WORD
        # First, check words seen 2+ times
        cdef Lexeme* word_ptr = <Lexeme*>self.vocab.get(string)
        cdef int split
        if word_ptr == NULL:
            split = self.find_split(string, length)
            if split != 0 and split != -1 and split < length:
                word_ptr = self.new_lexeme(string, string[:split])
                word_ptr.tail = <Lexeme*>self.lookup_chunk(string[split:])
            else:
                word_ptr = self.new_lexeme(string, string)
        return <Lexeme_addr>word_ptr

    cdef Orthography* lookup_orth(self, StringHash hashed, unicode lex):
        cdef Orthography* orth = <Orthography*>self.ortho[0][hashed]
        if orth == NULL:
            orth = self.new_orth(hashed, lex)
        return orth

    cdef Distribution* lookup_dist(self, StringHash hashed):
        cdef Distribution* dist = <Distribution*>self.distri[0][hashed]
        if dist == NULL:
            dist = self.new_dist(hashed)
        return dist

    cdef Lexeme* new_lexeme(self, unicode key, unicode string) except NULL:
        cdef Lexeme* word = <Lexeme*>calloc(1, sizeof(Lexeme))
        word.sic = hash(key)
        word.lex = hash(string)
        self.bacov[word.lex] = string
        self.bacov[word.sic] = key
        word.orth = self.lookup_orth(word.lex, string)
        word.dist = self.lookup_dist(word.lex)
        self.vocab.set(key, <size_t>word)
        return word   

    cdef Orthography* new_orth(self, StringHash hashed, unicode lex) except NULL:
        cdef unicode last3
        cdef unicode norm
        cdef unicode shape
        cdef int length 

        length = len(lex)
        orth = <Orthography*>calloc(1, sizeof(Orthography))
        orth.first = lex[0]
            
        orth.length = length
        orth.flags = set_orth_flags(lex, orth.length)
        orth.norm = hashed
        last3 = substr(lex, length - 3, length, length)
        orth.last3 = hash(last3)
        norm = get_normalized(lex, length)
        orth.norm = hash(norm)
        shape = get_word_shape(lex, length)
        orth.shape = hash(shape)

        self.bacov[orth.last3] = last3
        self.bacov[orth.norm] = norm
        self.bacov[orth.shape] = shape

        self.ortho[0][hashed] = <size_t>orth
        return orth

    cdef Distribution* new_dist(self, StringHash hashed) except NULL:
        dist = <Distribution*>calloc(1, sizeof(Distribution))
        self.distri[0][hashed] = <size_t>dist
        return dist

    cdef unicode unhash(self, StringHash hash_value):
        '''Fetch a string from the reverse index, given its hash value.'''
        return self.bacov[hash_value]

    cdef int find_split(self, unicode word, size_t length):
        return -1

    def load_tokenization(self, token_rules=None):
        cdef Lexeme* word
        cdef StringHash hashed
        for chunk, lex, tokens in token_rules:
            word = <Lexeme*>self.new_lexeme(chunk, lex)
            for i, lex in enumerate(tokens):
                token_string = '%s:@:%d:@:%s' % (chunk, i, lex)
                word.tail = <Lexeme*>self.new_lexeme(token_string, lex)
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
                word = self.new_lexeme(token_string, token_string)


cdef inline bint _is_whitespace(unsigned char c) nogil:
    if c == b' ':
        return True
    elif c == b'\n':
        return True
    elif c == b'\t':
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
