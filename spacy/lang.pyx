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
import json
from os import path


cdef class Language:
    def __cinit__(self, name):
        self.name = name
        self.cache = {}
        self.lexicon = Lexicon()
        self.load_tokenization(util.read_tokenization(name))

    cpdef list tokenize(self, unicode string):
        """Tokenize a string.

        The tokenization rules are defined in two places:

        * The data/<lang>/tokenization table, which handles special cases like contractions;
        * The appropriate :py:meth:`find_split` function, which is used to split
          off punctuation etc.

        Args:
            string (unicode): The string to be tokenized. 

        Returns:
            tokens (Tokens): A Tokens object, giving access to a sequence of LexIDs.
        """
        cdef list tokens = []
        cdef size_t length = len(string)
        cdef size_t start = 0
        cdef size_t i = 0
        for c in string:
            if c == ' ':
                if start < i:
                    tokens.extend(self._tokenize(string[start:i]))
                start = i + 1
            i += 1
        if start < i:
            tokens.extend(self._tokenize(string[start:]))
        return tokens

    cdef list _tokenize(self, unicode string):
        if string in self.cache:
            return self.cache[string]
        cdef list lexemes = []
        substrings = self._split(string)
        for i, substring in enumerate(substrings):
            lexemes.append(self.lookup(substring))
        self.cache[string] = lexemes
        return lexemes

    cpdef list _split(self, unicode string):
        """Find how to split a contiguous span of non-space characters into substrings.

        This method calls find_split repeatedly. Most languages will want to
        override _split_one, but it may be useful to override this instead.

        Args:
            chunk (unicode): The string to be split, e.g. u"Mike's!"

        Returns:
            substrings (list): The component substrings, e.g. [u"Mike", "'s", "!"].
        """
        substrings = []
        while string:
            split = self._split_one(string)
            if split == 0:
                substrings.append(string)
                break
            substrings.append(string[:split])
            string = string[split:]
        return substrings

    cpdef int _split_one(self, unicode word):
        return len(word)

    def load_special_tokenization(self, token_rules):
        '''Load special-case tokenization rules.

        Loads special-case tokenization rules into the Language.cache cache,
        read from data/<lang>/tokenization . The special cases are loaded before
        any language data is tokenized, giving these priority.  For instance,
        the English tokenization rules map "ain't" to ["are", "not"].

        Args:
            token_rules (list): A list of (chunk, tokens) pairs, where chunk is
                a string and tokens is a list of strings.
        '''
        for string, substrings in token_rules:
            lexemes = []
            for i, substring in enumerate(substrings):
                lexemes.append(self.lookup(substring))
            self.cache[string] = lexemes
 

cdef class Lexicon:
    def __cinit__(self):
        self.flag_checkers = []
        self.string_transforms = []
        self.lexicon = {}

    cpdef Lexeme lookup(self, unicode string):
        """Retrieve (or create, if not found) a Lexeme for a string, and return it.
    
        Args:
            string (unicode):  The string to be looked up. Must be unicode, not bytes.

        Returns:
            lexeme (Lexeme): A reference to a lexical type.
        """
        assert len(string) != 0
        if string in self.lexicon:
            return self.lexicon[string]
        
        prob = _pop_default(self.probs, string, 0.0)
        cluster = _pop_default(self.clusters, string, 0.0)
        case_stats = _pop_default(self.case_stats, string, {})
        tag_stats = _pop_default(self.tag_stats, string, {})

        cdef Lexeme word = Lexeme(string, prob, cluster, case_stats, tag_stats,
                                  self.flag_checkers, self.string_transformers)
        self.lexicon[string] = word
        return word

    def add_flag(self, flag_checker):
        cdef unicode string
        cdef Lexeme word
        flag_id = len(self.flag_checkers)
        for string, word in self.lexicon.items():
            if flag_checker(string, word.prob, {}):
                word.set_flag(flag_id)
        self.flag_checkers.append(flag_checker)
        return flag_id

    def add_transform(self, string_transform):
        self.string_transformers.append(string_transform)
        return len(self.string_transformers) - 1

    def load_probs(self, location):
        """Load unigram probabilities.
        """
        self.probs = json.load(location)
        
        cdef Lexeme word
        cdef unicode string

        for string, word in self.lexicon.items():
            prob = _pop_default(self.probs, string, 0.0)
            word.prob = prob

    def load_clusters(self, location):
        self.probs = json.load(location)
        
        cdef Lexeme word
        cdef unicode string

        for string, word in self.lexicon.items():
            cluster = _pop_default(self.cluster, string, 0)
            word.cluster = cluster

    def load_stats(self, location):
        """Load distributional stats.
        """
        raise NotImplementedError


def _pop_default(dict d, key, default):
    return d.pop(key) if key in d else default
