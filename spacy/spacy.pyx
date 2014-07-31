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


DEF MAX_HAPPAX = 1000000


cdef class Language:
    def __cinit__(self, name):
        self.name = name
        self.bacov = {}
        self.happax = new SparseVocab()
        self.vocab = new Vocab()
        self.ortho = new Vocab()
        self.distri = new Vocab()
        self.happax[0].set_deleted_key(0)
        self.vocab[0].set_empty_key(0)
        self.distri[0].set_empty_key(0)
        self.ortho[0].set_empty_key(0)
        self.vocab[0].set_deleted_key(1)
        self.distri[0].set_deleted_key(1)
        self.ortho[0].set_deleted_key(1)
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
        return mrmr.hash64(<Py_UNICODE*>s, length * sizeof(Py_UNICODE), 0)

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
        # First, check words seen 2+ times
        cdef Lexeme* word_ptr = <Lexeme*>self.vocab[0][hashed]
        if word_ptr == NULL:
            # Now check words seen exactly once
            word_ptr = <Lexeme*>self.happax[0][hashed]
            if word_ptr == NULL:
                start = self.find_split(string, length) if start == -1 else start
                word_ptr = self._add(hashed, string, start, length)
            else:
                # Second time word seen, move to vocab
                self.vocab[0][hashed] = <Lexeme_addr>word_ptr
                self.happax[0].erase(hashed)
        return <Lexeme_addr>word_ptr

    cdef Lexeme* _add(self, StringHash hashed, unicode string, int split, size_t length):
        cdef size_t i
        cdef sparse_hash_map[StringHash, size_t].iterator it
        cdef pair[StringHash, size_t] last_elem
        if self.happax[0].size() >= MAX_HAPPAX:
            # Delete last element.
            last_elem = deref(self.happax[0].end())
            free(<Orthography*>self.ortho[0][last_elem.first])
            free(<Distribution*>self.distri[0][last_elem.first])
            free(<Lexeme*>last_elem.second)
            self.happax[0].erase(last_elem.first)
            self.ortho[0].erase(last_elem.first)
            self.distri[0].erase(last_elem.first)
        word = self.init_lexeme(string, hashed, split, length)
        self.happax[0][hashed] = <Lexeme_addr>word
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

    cdef Lexeme* init_lexeme(self, unicode string, StringHash hashed,
                             int split, size_t length):
        cdef Lexeme* word = <Lexeme*>calloc(1, sizeof(Lexeme))
    
        word.sic = hashed
    
        cdef unicode tail_string
        cdef unicode lex 
        if split != 0 and split < length:
            lex = substr(string, 0, split, length)
            tail_string = substr(string, split, length, length)
        else:
            lex = string
            tail_string = ''
    
        word.lex = self.hash_string(lex, len(lex))
        self.bacov[word.lex] = lex
        word.orth = <Orthography*>self.ortho[0][word.lex]
        if word.orth == NULL:
            word.orth = self.init_orth(word.lex, lex)
        word.dist = <Distribution*>self.distri[0][word.lex]
    
        # Now recurse, and deal with the tail
        if tail_string:
            word.tail = <Lexeme*>self.lookup(-1, tail_string, len(tail_string))
        return word

    cdef Orthography* init_orth(self, StringHash hashed, unicode lex):
        cdef Orthography* orth = <Orthography*>calloc(1, sizeof(Orthography))
        orth.first = <Py_UNICODE>lex[0]

        cdef int length = len(lex)
        
        orth.flags = set_orth_flags(lex, length)
        
        cdef unicode last3 = substr(lex, length - 3, length, length)
        cdef unicode norm = get_normalized(lex, length)
        cdef unicode shape = get_word_shape(lex, length)

        orth.last3 = self.hash_string(last3, len(last3))
        orth.shape = self.hash_string(shape, len(shape))
        orth.norm = self.hash_string(norm, len(norm))

        self.bacov[orth.last3] = last3
        self.bacov[orth.shape] = shape
        self.bacov[orth.norm] = norm

        self.ortho[0][hashed] = <size_t>orth
        return orth


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
