# cython: profile=True
# cython: embedsignature=True
"""Common classes and utilities across languages.

Provides the main implementation for the spacy tokenizer. Specific languages
subclass the Language class, over-writing the tokenization rules as necessary.
Special-case tokenization rules are read from data/<lang>/tokenization .
"""
from __future__ import unicode_literals

from libc.stdlib cimport calloc, free

import json
from os import path

from .util import read_lang_data


cdef class Language:
    """Base class for language-specific tokenizers.

    Most subclasses will override the _split or _split_one methods, which take
    a string of non-whitespace characters and output a list of strings.  This
    function is called by _tokenize, which sits behind a cache and turns the
    list of strings into Lexeme objects via the Lexicon. Most languages will not
    need to override _tokenize or tokenize.

    The language is supplied a list of boolean functions, used to compute flag
    features. These are passed to the language's Lexicon object.

    The language's name is used to look up default data-files, found in data/<name.
    """
    def __cinit__(self, name, string_features, flag_features):
        if flag_features is None:
            flag_features = []
        if string_features is None:
            string_features = []
        self.name = name
        self.cache = {}
        lang_data = read_lang_data(name)
        rules, words, probs, clusters, case_stats, tag_stats = lang_data
        self.lexicon = Lexicon(words, probs, clusters, case_stats, tag_stats,
                               string_features, flag_features)
        self._load_special_tokenization(rules)

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
        if not string:
            return []
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
        assert tokens
        return tokens

    cpdef Lexeme lookup(self, unicode string):
        """Retrieve (or create, if not found) a Lexeme for a string, and return it.
    
        Args:
            string (unicode): The string to be looked up. Must be unicode, not bytes.

        Returns:
            lexeme (Lexeme): A reference to a lexical type.
        """
        return self.lexicon.lookup(string)

    cdef list _tokenize(self, unicode string):
        if string in self.cache:
            return self.cache[string]
        cdef list lexemes = []
        substrings = self._split(string)
        for i, substring in enumerate(substrings):
            lexemes.append(self.lexicon.lookup(substring))
        self.cache[string] = lexemes
        return lexemes

    cdef list _split(self, unicode string):
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

    cdef int _split_one(self, unicode word):
        return len(word)

    def _load_special_tokenization(self, token_rules):
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
                lexemes.append(self.lexicon.lookup(substring))
            self.cache[string] = lexemes
 

cdef class Lexicon:
    def __cinit__(self, words, probs, clusters, case_stats, tag_stats,
                  string_features, flag_features):
        self._flag_features = flag_features
        self._string_features = string_features
        self._dict = {}
        cdef Lexeme word
        for string in words:
            word = Lexeme(string, probs.get(string, 0.0), clusters.get(string, 0),
                          case_stats.get(string, {}), tag_stats.get(string, {}),
                          self._string_features, self._flag_features)
            self._dict[string] = word

    cpdef Lexeme lookup(self, unicode string):
        """Retrieve (or create, if not found) a Lexeme for a string, and return it.
    
        Args
            string (unicode):  The string to be looked up. Must be unicode, not bytes.

        Returns:
            lexeme (Lexeme): A reference to a lexical type.
        """
        assert len(string) != 0
        if string in self._dict:
            return self._dict[string]
        
        cdef Lexeme word = Lexeme(string, 0, 0, {}, {}, self._string_features,
                                  self._flag_features)
        self._dict[string] = word
        return word
