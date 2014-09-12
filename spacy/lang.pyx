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
import random
from os import path

from .util import read_lang_data
from spacy.tokens import Tokens
from spacy.lexeme cimport LexemeC, lexeme_init
from murmurhash.mrmr cimport hash64


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
        self.cache.set_empty_key(0)
        self.specials.set_empty_key(0)
        lang_data = read_lang_data(name)
        rules, words, probs, clusters, case_stats, tag_stats = lang_data
        self.lexicon = Lexicon(words, probs, clusters, case_stats, tag_stats,
                               string_features, flag_features)
        self._load_special_tokenization(rules)
        self.tokens_class = Tokens

    def __dealloc__(self):
        cdef uint64_t hashed
        cdef size_t lex_addr
        for (hashed, lex_addr) in self.specials:
            free(<LexemeC*>lex_addr)

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
        cdef Py_UNICODE* chars = string
        cdef Py_UNICODE c
        cdef String span
        for i in range(length):
            c = chars[i]
            if Py_UNICODE_ISSPACE(c) == 1:
                if start < i:
                    string_from_slice(&span, chars, start, i)
                    self._tokenize(tokens, &span)
                start = i + 1
        i += 1
        if start < i:
            string_from_slice(&span, chars, start, i)
            self._tokenize(tokens, &span)
        return tokens

    cdef _tokenize(self, Tokens tokens, String* string):
        cdef LexemeC** lexemes = <LexemeC**>self.specials[string.key]
        if lexemes == NULL:
            lexemes = <LexemeC**>self.cache[string.key]
        if lexemes != NULL:
            _extend_tokens(tokens, lexemes)
            return 0
        cdef uint64_t hashed = string.key

        cdef size_t first_token = tokens.length
        cdef size_t start = 0
        cdef size_t length = string.n
        cdef String prefix
        while start < length:
            split = self._split_one(string.chars, string.n)
            string_slice_prefix(string, &prefix, split)
            lexemes = <LexemeC**>self.specials[prefix.key]
            if lexemes != NULL:
                _extend_tokens(tokens, lexemes)
            else:
                tokens.push_back(<LexemeC*>self.lexicon.get(&prefix))
            start += prefix.n
        lexemes = <LexemeC**>calloc(tokens.length - first_token, sizeof(LexemeC*))
        for i, j in enumerate(range(first_token, tokens.length)):
            lexemes[i] = tokens.lexemes[j]
        self.cache[hashed] = <size_t>lexemes

    cdef int _split_one(self, Py_UNICODE* characters, size_t length):
        return length

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
        cdef uint64_t hashed
        cdef String string
        for uni_string, substrings in token_rules:
            lexemes = <LexemeC**>calloc(len(substrings) + 1, sizeof(LexemeC*))
            for i, substring in enumerate(substrings):
                string_from_unicode(&string, substring)
                lexemes[i] = <LexemeC*>self.lexicon.get(&string)
            lexemes[i + 1] = NULL
            string_from_unicode(&string, uni_string)
            self.specials[string.key] = <size_t>lexemes


cdef _extend_tokens(Tokens tokens, LexemeC** lexemes):
    cdef size_t i = 0
    while lexemes[i] != NULL:
        tokens.push_back(lexemes[i])
        i += 1


cdef class Lexicon:
    def __cinit__(self, words, probs, clusters, case_stats, tag_stats,
                  string_features, flag_features):
        self._flag_features = flag_features
        self._string_features = string_features
        self._dict.set_empty_key(0)
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

    cdef size_t get(self, String* string):
        cdef LexemeC* lexeme = <LexemeC*>self._dict[string.key]
        if lexeme != NULL:
            return <size_t>lexeme
        
        cdef unicode uni_string = string.chars[:string.n]
        views = [string_view(uni_string, 0.0, 0, {}, {})
                 for string_view in self._string_features]
        flags = set()
        for i, flag_feature in enumerate(self._flag_features):
            if flag_feature(uni_string, 0.0, {}, {}):
                flags.add(i)
 
        lexeme = lexeme_init(uni_string, 0, 0, views, flags)
        self._dict[string.key] = <size_t>lexeme
        self.size += 1
        return <size_t>lexeme

    cpdef Lexeme lookup(self, unicode uni_string):
        """Retrieve (or create, if not found) a Lexeme for a string, and return it.
    
        Args
            string (unicode):  The string to be looked up. Must be unicode, not bytes.

        Returns:
            lexeme (Lexeme): A reference to a lexical type.
        """
        cdef String string
        string_from_unicode(&string, uni_string)
        cdef size_t lexeme = self.get(&string)
        return Lexeme(lexeme)


cdef string_from_unicode(String* s, unicode uni):
    string_from_slice(s, <Py_UNICODE*>uni, 0, len(uni))


cdef string_from_slice(String* s, Py_UNICODE* chars, size_t start, size_t end):
    s.chars = &chars[start]
    s.n = end - start
    s.key = hash64(s.chars, s.n * sizeof(Py_UNICODE), 0)


cdef string_slice_prefix(String* s, String* prefix, size_t n):
    assert s.n >= n
    string_from_slice(prefix, s.chars, 0, n)
    s.chars += n
    s.n -= n
    s.key = hash64(s.chars, s.n * sizeof(Py_UNICODE), 0)
