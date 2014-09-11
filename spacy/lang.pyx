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
from spacy.tokens import Tokens
from spacy.lexeme cimport LexemeC, lexeme_init


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
        self.tokens_class = Tokens

    property nr_types:
        def __get__(self):
            """Return the number of lexical types in the vocabulary"""
            return self.lexicon.size

    cpdef Lexeme lookup(self, unicode string):
        """Retrieve (or create, if not found) a Lexeme for a string, and return it.
    
        Args:
            string (unicode): The string to be looked up. Must be unicode, not bytes.

        Returns:
            lexeme (Lexeme): A reference to a lexical type.
        """
        return self.lexicon.lookup(string)

    cpdef Tokens tokenize(self, unicode string):
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
        cdef size_t length = len(string)
        cdef Tokens tokens = self.tokens_class(length)
        if length == 0:
            return tokens

        cdef size_t start = 0
        cdef size_t i = 0
        for c in string:
            if c == ' ':
                if start < i:
                    self._tokenize(tokens, string[start:i])
                start = i + 1
            i += 1
        if start < i:
            self._tokenize(tokens, string[start:i])
        return tokens

    cdef _tokenize(self, Tokens tokens, unicode string):
        cdef LexemeC** lexemes
        if string in self.cache:
            lexemes = <LexemeC**><size_t>self.cache[string]
        else:
            substrings = self._split(string)
            lexemes = <LexemeC**>calloc(len(substrings) + 1, sizeof(LexemeC*))
            for i, substring in enumerate(substrings):
                lexemes[i] = <LexemeC*>self.lexicon.get(substring)
            lexemes[i + 1] = NULL
            self.cache[string] = <size_t>lexemes
        cdef LexemeC* lexeme
        i = 0
        while lexemes[i] != NULL:
            tokens.push_back(lexemes[i])
            i += 1

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
        cdef LexemeC** lexemes
        for string, substrings in token_rules:
            lexemes = <LexemeC**>calloc(len(substrings) + 1, sizeof(LexemeC*))
            for i, substring in enumerate(substrings):
                lexemes[i] = <LexemeC*>self.lexicon.get(substring)
            lexemes[i + 1] = NULL
            self.cache[string] = <size_t>lexemes
 

cdef class Lexicon:
    def __cinit__(self, words, probs, clusters, case_stats, tag_stats,
                  string_features, flag_features):
        self._flag_features = flag_features
        self._string_features = string_features
        self._dict = {}
        self.size = 0
        cdef Lexeme word
        for string in words:
            prob = probs.get(string, 0.0)
            cluster = clusters.get(string, 0.0)
            cases = case_stats.get(string, {})
            tags = tag_stats.get(string, {})
            views = [string_view(string, prob, cluster, cases, tags)
                     for string_view in self._string_features]
            flags = set()
            for i, flag_feature in enumerate(self._flag_features):
                if flag_feature(string, prob, cluster, cases, tags):
                    flags.add(i)
            lexeme = lexeme_init(string, prob, cluster, views, flags)
            self._dict[string] = <size_t>lexeme
            self.size += 1

    cdef size_t get(self, unicode string):
        cdef LexemeC* lexeme
        assert len(string) != 0
        if string in self._dict:
            return self._dict[string]
        
        views = [string_view(string, 0.0, 0, {}, {})
                 for string_view in self._string_features]
        flags = set()
        for i, flag_feature in enumerate(self._flag_features):
            if flag_feature(string, 0.0, {}, {}):
                flags.add(i)
 
        lexeme = lexeme_init(string, 0, 0, views, flags)
        self._dict[string] = <size_t>lexeme
        self.size += 1
        return <size_t>lexeme

    cpdef Lexeme lookup(self, unicode string):
        """Retrieve (or create, if not found) a Lexeme for a string, and return it.
    
        Args
            string (unicode):  The string to be looked up. Must be unicode, not bytes.

        Returns:
            lexeme (Lexeme): A reference to a lexical type.
        """
        cdef size_t lexeme = self.get(string)
        return Lexeme(lexeme)
