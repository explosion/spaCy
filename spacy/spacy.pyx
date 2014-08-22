# cython: profile=True
# cython: embedsignature=True
"""Common classes and utilities across languages.

Provides the main implementation for the spacy tokenizer. Specific languages
subclass the Language class, over-writing the tokenization rules as necessary.
Special-case tokenization rules are read from data/<lang>/tokenization .
"""

 
from __future__ import unicode_literals

from libc.stdlib cimport calloc, free
from libcpp.pair cimport pair
from cython.operator cimport dereference as deref

from . import util
from os import path

TAGS = {}
DIST_FLAGS = {}

cdef class Language:
    view_funcs = []
    def __cinit__(self, name):
        self.name = name
        self.bacov = {}
        self.chunks = {}
        self.vocab = {}
        self.load_tokenization(util.read_tokenization(name))
        self.load_dist_info(util.read_dist_info(name))

    cpdef list tokenize(self, unicode string):
        """Tokenize.

        Split the string into tokens.

        Args:
            string (unicode): The string to split.

        Returns:
            tokens (Tokens): A Tokens object.
        """
        cdef list chunk
        cdef list tokens = []
        cdef size_t length = len(string)
        cdef size_t start = 0
        cdef size_t i = 0
        for c in string:
            if _is_whitespace(c):
                if start < i:
                    chunk = self.lookup_chunk(string[start:i])
                    tokens.extend(chunk)
                start = i + 1
            i += 1
        if start < i:
            chunk = self.lookup_chunk(string[start:])
            tokens.extend(chunk)
        return tokens

    cdef Word lookup(self, unicode string):
        assert len(string) != 0
        cdef Word word 
        cdef StringHash h = hash(string)
        if h in self.vocab:
            word = self.vocab[h]
        else:
            word = self.new_lexeme(string)
        return word

    cdef list lookup_chunk(self, unicode string):
        cdef StringHash h = hash(string)
        cdef list chunk
        cdef size_t chunk_id
        if h in self.chunks:
            chunk = self.chunks[h]
        else:
            chunk = self.new_chunk(string, self.find_substrings(string))
        return chunk

    cdef list new_chunk(self, unicode string, list substrings):
        chunk = []
        for i, substring in enumerate(substrings):
            chunk.append(self.lookup(substring))
        cdef StringHash h = hash(string)
        self.chunks[h] = chunk
        return chunk

    cdef Word new_lexeme(self, unicode string):
        string_views = [view_func(string) for view_func in self.view_funcs]
        word = Word(string.encode('utf8'), string_views)
        self.bacov[word.lex] = string
        self.vocab[word.lex] = word
        return word

    """
    def add_view_funcs(self, list view_funcs):
        self.view_funcs.extend(view_funcs)
        cdef size_t nr_views = len(self.view_funcs)

        cdef unicode view
        cdef StringHash hashed
        cdef StringHash key
        cdef unicode string
        cdef LexID lex_id
        cdef Lexeme* word

        for key, lex_id in self.vocab.items():
            word = <Lexeme*>lex_id
            free(word.string_views)
            word.string_views = <StringHash*>calloc(nr_views, sizeof(StringHash))
            string = word.string[:word.length].decode('utf8')
            for i, view_func in enumerate(self.view_funcs):
                view = view_func(string)
                hashed = hash(view)
                word.string_views[i] = hashed
                self.bacov[hashed] = view
    """

    cpdef unicode unhash(self, StringHash hash_value):
        '''Fetch a string from the reverse index, given its hash value.'''
        return self.bacov[hash_value]

    cpdef list find_substrings(self, unicode chunk):
        """Find how to split a chunk into substrings.

        This method calls find_split repeatedly. Most languages will want to
        override find_split, but it may be useful to override this instead.

        Args:
            chunk (unicode): The string to be split, e.g. u"Mike's!"

        Returns:
            substrings (list): The component substrings, e.g. [u"Mike", "'s", "!"].
        """
        substrings = []
        while chunk:
            split = self.find_split(chunk)
            if split == 0:
                substrings.append(chunk)
                break
            substrings.append(chunk[:split])
            chunk = chunk[split:]
        return substrings

    cdef int find_split(self, unicode word):
        return len(word)

    cdef int set_orth(self, unicode string, Word word):
        pass

    def load_tokenization(self, token_rules):
        '''Load special-case tokenization rules.

        Loads special-case tokenization rules into the Language.chunk cache,
        read from data/<lang>/tokenization . The special cases are loaded before
        any language data is tokenized, giving these priority.  For instance,
        the English tokenization rules map "ain't" to ["are", "not"].

        Args:
            token_rules (list): A list of (chunk, tokens) pairs, where chunk is
                a string and tokens is a list of strings.
        '''
        for chunk, tokens in token_rules:
            self.new_chunk(chunk, tokens)

    def load_dist_info(self, dist_info):
        '''Load distributional information for the known lexemes of the language.

        The distributional information is read from data/<lang>/dist_info.json .
        It contains information like the (smoothed) unigram log probability of
        the word, how often the word is found upper-cased, how often the word
        is found title-cased, etc.
        '''
        cdef unicode string
        cdef dict word_dist
        cdef Word w
        for string, word_dist in dist_info.items():
            w = self.lookup(string)
            w.prob = word_dist.prob
            w.cluster = word_dist.cluster
            for flag in word_dist.flags:
                w.dist_flags |= DIST_FLAGS[flag]
            for tag in word_dist.tagdict:
                w.possible_tags |= TAGS[tag]


cdef inline bint _is_whitespace(Py_UNICODE c) nogil:
    if c == ' ':
        return True
    elif c == '\n':
        return True
    elif c == '\t':
        return True
    else:
        return False


#cdef inline int _extend(Tokens tokens, Lexeme** chunk) nogil:
#    cdef size_t i = 0
#    while chunk[i] != NULL:
#        tokens.vctr[0].push_back(<Lexeme_addr>chunk[i])
#        tokens.length += 1
#        i += 1
