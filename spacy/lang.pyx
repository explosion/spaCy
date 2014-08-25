# cython: profile=True
# cython: embedsignature=True
"""Common classes and utilities across languages.

Provides the main implementation for the spacy tokenizer. Specific languages
subclass the Language class, over-writing the tokenization rules as necessary.
Special-case tokenization rules are read from data/<lang>/tokenization .
"""

 
from __future__ import unicode_literals

from libc.stdlib cimport calloc, free

from . import util
from os import path


cdef class Language:
    view_funcs = []
    def __cinit__(self, name):
        self.name = name
        self.blobs = {}
        self.lexicon = {}
        self.load_tokenization(util.read_tokenization(name))
        self.load_dist_info(util.read_dist_info(name))

    cpdef list tokenize(self, unicode string):
        """Tokenize.

        Split the string into tokens.

        Args:
            string (unicode): The string to split.

        Returns:
            tokens (list): A list of Lexeme objects.
        """
        cdef list blob
        cdef list tokens = []
        cdef size_t length = len(string)
        cdef size_t start = 0
        cdef size_t i = 0
        for c in string:
            if c == ' ':
                if start < i:
                    blob = self.lookup_blob(string[start:i])
                    tokens.extend(blob)
                start = i + 1
            i += 1
        if start < i:
            chunk = self.lookup_blob(string[start:])
            tokens.extend(chunk)
        return tokens

    cdef Lexeme lookup(self, unicode string):
        assert len(string) != 0
        cdef Word word 
        if string in self.vocab:
            word = self.vocab[string]
        else:
            word = self.new_lexeme(string)
        return word

    cdef list lookup_blob(self, unicode string):
        cdef list chunk
        cdef size_t blob_id
        if string in self.blobs:
            blob = self.blobs[string]
        else:
            blob = self.new_blob(string, self.find_substrings(string))
        return chunk

    cdef list new_blob(self, unicode string, list substrings):
        blob = []
        for i, substring in enumerate(substrings):
            blob.append(self.lookup(substring))
        self.blobs[string] = chunk
        return blob

    cdef Word new_lexeme(self, unicode string):
        # TODO
        #lexeme = Lexeme(string.encode('utf8'), string_views)
        #return lexeme

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

    cpdef list find_substrings(self, unicode blob):
        """Find how to split a chunk into substrings.

        This method calls find_split repeatedly. Most languages will want to
        override find_split, but it may be useful to override this instead.

        Args:
            chunk (unicode): The string to be split, e.g. u"Mike's!"

        Returns:
            substrings (list): The component substrings, e.g. [u"Mike", "'s", "!"].
        """
        substrings = []
        while blob:
            split = self.find_split(blob)
            if split == 0:
                substrings.append(blob)
                break
            substrings.append(blob[:split])
            blob = blob[split:]
        return substrings

    cdef int find_split(self, unicode word):
        return len(word)

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
