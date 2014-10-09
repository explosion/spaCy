# cython: profile=True
# cython: embedsignature=True
"""Common classes and utilities across languages.

Provides the main implementation for the spacy tokenizer. Specific languages
subclass the Language class, over-writing the tokenization rules as necessary.
Special-case tokenization rules are read from data/<lang>/tokenization .
"""
from __future__ import unicode_literals

import json
import random
from os import path
import re

from .util import read_lang_data
from spacy.tokens import Tokens
from spacy.lexeme cimport LexemeC, lexeme_init
from murmurhash.mrmr cimport hash64

from cpython.ref cimport Py_INCREF

from cymem.cymem cimport Pool

from cython.operator cimport preincrement as preinc
from cython.operator cimport dereference as deref


from preshed.maps cimport PreshMap
from spacy import orth
from spacy import util


cdef enum Flags:
    Flag_IsAlpha
    Flag_IsAscii
    Flag_IsDigit
    Flag_IsLower
    Flag_IsPunct
    Flag_IsSpace
    Flag_IsTitle
    Flag_IsUpper

    Flag_CanAdj
    Flag_CanAdp
    Flag_CanAdv
    Flag_CanConj
    Flag_CanDet
    Flag_CanNoun
    Flag_CanNum
    Flag_CanPdt
    Flag_CanPos
    Flag_CanPron
    Flag_CanPrt
    Flag_CanPunct
    Flag_CanVerb

    Flag_OftLower
    Flag_OftTitle
    Flag_OftUpper
    Flag_N


cdef enum Views:
    View_CanonForm
    View_WordShape
    View_NonSparse
    View_Asciied
    View_N



# Assign the flag and view functions by enum value.
# This is verbose, but it ensures we don't get nasty order sensitivities.
STRING_VIEW_FUNCS = [None] * View_N
STRING_VIEW_FUNCS[View_CanonForm] = orth.canon_case
STRING_VIEW_FUNCS[View_WordShape] = orth.word_shape
STRING_VIEW_FUNCS[View_NonSparse] = orth.non_sparse
STRING_VIEW_FUNCS[View_Asciied] = orth.asciied

FLAG_FUNCS = [None] * Flag_N
FLAG_FUNCS[Flag_IsAlpha] = orth.is_alpha
FLAG_FUNCS[Flag_IsAscii] = orth.is_ascii
FLAG_FUNCS[Flag_IsDigit] = orth.is_digit
FLAG_FUNCS[Flag_IsLower] = orth.is_lower
FLAG_FUNCS[Flag_IsPunct] = orth.is_punct
FLAG_FUNCS[Flag_IsSpace] = orth.is_space
FLAG_FUNCS[Flag_IsTitle] = orth.is_title
FLAG_FUNCS[Flag_IsUpper] = orth.is_upper

FLAG_FUNCS[Flag_CanAdj] = orth.can_tag('ADJ')
FLAG_FUNCS[Flag_CanAdp] = orth.can_tag('ADP')
FLAG_FUNCS[Flag_CanAdv] = orth.can_tag('ADV')
FLAG_FUNCS[Flag_CanConj] = orth.can_tag('CONJ')
FLAG_FUNCS[Flag_CanDet] = orth.can_tag('DET')
FLAG_FUNCS[Flag_CanNoun] = orth.can_tag('NOUN')
FLAG_FUNCS[Flag_CanNum] = orth.can_tag('NUM')
FLAG_FUNCS[Flag_CanPdt] = orth.can_tag('PDT')
FLAG_FUNCS[Flag_CanPos] = orth.can_tag('POS')
FLAG_FUNCS[Flag_CanPron] = orth.can_tag('PRON')
FLAG_FUNCS[Flag_CanPrt] = orth.can_tag('PRT')
FLAG_FUNCS[Flag_CanPunct] = orth.can_tag('PUNCT')
FLAG_FUNCS[Flag_CanVerb] = orth.can_tag('VERB')

FLAG_FUNCS[Flag_OftLower] = orth.oft_case('lower', 0.7)
FLAG_FUNCS[Flag_OftTitle] = orth.oft_case('title', 0.7)
FLAG_FUNCS[Flag_OftUpper] = orth.oft_case('upper', 0.7)




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
    fl_is_alpha = Flag_IsAlpha
    fl_is_digit = Flag_IsDigit
    v_shape = View_WordShape

    def __cinit__(self, name, user_string_features, user_flag_features):
        self.name = name
        self._mem = Pool()
        self.cache = PreshMap(2 ** 25)
        self.specials = PreshMap(2 ** 16)
        lang_data = util.read_lang_data(name)
        rules, prefix, suffix, words, probs, clusters, case_stats, tag_stats = lang_data
        self.prefix_re = re.compile(prefix)
        self.suffix_re = re.compile(suffix)
        self.lexicon = Lexicon(words, probs, clusters, case_stats, tag_stats,
                               STRING_VIEW_FUNCS + user_string_features,
                               FLAG_FUNCS + user_flag_features)
        self._load_special_tokenization(rules)

    def __dealloc__(self):
        pass

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
        cdef Tokens tokens = Tokens(length)
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
                    try:
                        self._tokenize(tokens.v, &span)
                    except MemoryError:
                        print chars[start:i]
                        raise
                start = i + 1
        i += 1
        if start < i:
            string_from_slice(&span, chars, start, i)
            self._tokenize(tokens.v, &span)
        return tokens

    cdef int _tokenize(self, vector[LexemeC*] *tokens_v, String* string) except -1:
        cdef size_t i
        lexemes = <LexemeC**>self.cache.get(string.key)
        if lexemes != NULL:
            i = 0
            while lexemes[i] != NULL:
                tokens_v.push_back(lexemes[i])
                i += 1
            return 0

        cdef uint64_t orig_key = string.key
        cdef size_t orig_size = tokens_v.size()

        cdef vector[LexemeC*] prefixes
        cdef vector[LexemeC*] suffixes

        cdef String prefix
        cdef String suffix
        cdef String minus_pre
        cdef String minus_suf
        cdef size_t last_size = 0
        while string.n != 0 and string.n != last_size:
            last_size = string.n
            pre_len = self._find_prefix(string.chars, string.n)
            if pre_len != 0:
                string_from_slice(&prefix, string.chars, 0, pre_len)
                string_from_slice(&minus_pre, string.chars, pre_len, string.n)
                # Check whether we've hit a special-case
                if minus_pre.n >= 1 and self.specials.get(minus_pre.key) != NULL:
                    string = &minus_pre
                    prefixes.push_back(self.lexicon.get(&prefix))
                    break
            suf_len = self._find_suffix(string.chars, string.n)
            if suf_len != 0:
                string_from_slice(&suffix, string.chars, string.n - suf_len, string.n)
                string_from_slice(&minus_suf, string.chars, 0, string.n - suf_len)
                # Check whether we've hit a special-case
                if minus_suf.n >= 1 and self.specials.get(minus_suf.key) != NULL:
                    string = &minus_suf
                    suffixes.push_back(self.lexicon.get(&suffix))
                    break

            if pre_len and suf_len and (pre_len + suf_len) <= string.n:
                string_from_slice(string, string.chars, pre_len, string.n - suf_len)
                prefixes.push_back(self.lexicon.get(&prefix))
                suffixes.push_back(self.lexicon.get(&suffix))
            elif pre_len:
                string = &minus_pre
                prefixes.push_back(self.lexicon.get(&prefix))
            elif suf_len:
                string = &minus_suf
                suffixes.push_back(self.lexicon.get(&suffix))

            if self.specials.get(string.key):
                break

        self._attach_tokens(tokens_v, string, &prefixes, &suffixes)
        self._save_cached(tokens_v, orig_key, orig_size)

    cdef int _check_cache(self, vector[LexemeC*] *tokens, String* string) except -1:
        lexemes = <LexemeC**>self.cache.get(string.key)
        cdef size_t i = 0
        if lexemes != NULL:
            while lexemes[i] != NULL:
                tokens.push_back(lexemes[i])
                i += 1
            string.n = 0
            string.key = 0
            string.chars = NULL

    cdef int _attach_tokens(self, vector[LexemeC*] *tokens, String* string,
                            vector[LexemeC*] *prefixes,
                            vector[LexemeC*] *suffixes) except -1:
        cdef size_t i
        cdef LexemeC** lexemes
        cdef LexemeC* lexeme
        for lexeme in deref(prefixes):
            tokens.push_back(lexeme)
        if string.n != 0:
            lexemes = <LexemeC**>self.specials.get(string.key)
            if lexemes != NULL:
                i = 0 
                while lexemes[i] != NULL:
                    tokens.push_back(lexemes[i])
                    i += 1
            else:
                tokens.push_back(self.lexicon.get(string))
        cdef vector[LexemeC*].reverse_iterator it = suffixes.rbegin()
        while it != suffixes.rend():
            tokens.push_back(deref(it))
            preinc(it)

    cdef int _save_cached(self, vector[LexemeC*] *tokens,
                          uint64_t key, size_t n) except -1:
        assert tokens.size() > n
        lexemes = <LexemeC**>self._mem.alloc((tokens.size() - n) + 1, sizeof(LexemeC**))
        cdef size_t i, j
        for i, j in enumerate(range(n, tokens.size())):
            lexemes[i] = tokens.at(j)
        lexemes[i + 1] = NULL
        self.cache.set(key, lexemes)
    
    cdef int _find_prefix(self, Py_UNICODE* chars, size_t length) except -1:
        cdef unicode string = chars[:length]
        match = self.prefix_re.search(string)
        if match is None:
            return 0
        else:
            return match.end() - match.start()

    cdef int _find_suffix(self, Py_UNICODE* chars, size_t length):
        cdef unicode string = chars[:length]
        match = self.suffix_re.search(string)
        if match is None:
            return 0
        else:
            return match.end() - match.start()

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
            lexemes = <LexemeC**>self._mem.alloc(len(substrings) + 1, sizeof(LexemeC*))
            for i, substring in enumerate(substrings):
                string_from_unicode(&string, substring)
                lexemes[i] = <LexemeC*>self.lexicon.get(&string)
            lexemes[i + 1] = NULL
            string_from_unicode(&string, uni_string)
            self.specials.set(string.key, lexemes)
            self.cache.set(string.key, lexemes)


cdef class Lexicon:
    def __cinit__(self, words, probs, clusters, case_stats, tag_stats,
                  string_features, flag_features):
        self._mem = Pool()
        self._flag_features = flag_features
        self._string_features = string_features
        self._dict = PreshMap(2 ** 20)
        self.size = 0
        cdef String string
        for uni_string in words:
            prob = probs.get(uni_string, 0.0)
            cluster = clusters.get(uni_string, 0.0)
            cases = case_stats.get(uni_string, {})
            tags = tag_stats.get(uni_string, {})
            views = [string_view(uni_string, prob, cluster, cases, tags)
                     for string_view in self._string_features]
            flags = set()
            for i, flag_feature in enumerate(self._flag_features):
                if flag_feature(uni_string, prob, cluster, cases, tags):
                    flags.add(i)
            lexeme = lexeme_init(self._mem, self.size, uni_string, prob, cluster, views, flags)
            string_from_unicode(&string, uni_string)
            self._dict.set(string.key, lexeme)
            self.size += 1

    cdef LexemeC* get(self, String* string) except NULL:
        cdef LexemeC* lexeme
        lexeme = <LexemeC*>self._dict.get(string.key)
        if lexeme != NULL:
            return lexeme
        
        cdef unicode uni_string = string.chars[:string.n]
        views = [string_view(uni_string, 0.0, 0, {}, {})
                 for string_view in self._string_features]
        flags = set()
        for i, flag_feature in enumerate(self._flag_features):
            if flag_feature(uni_string, 0.0, {}, {}):
                flags.add(i)
 
        lexeme = lexeme_init(self._mem, self.size, uni_string, 0, 0, views, flags)
        self._dict.set(string.key, lexeme)
        self.size += 1
        return lexeme

    cpdef Lexeme lookup(self, unicode uni_string):
        """Retrieve (or create, if not found) a Lexeme for a string, and return it.
    
        Args
            string (unicode):  The string to be looked up. Must be unicode, not bytes.

        Returns:
            lexeme (Lexeme): A reference to a lexical type.
        """
        cdef String string
        string_from_unicode(&string, uni_string)
        cdef LexemeC* lexeme = self.get(&string)
        return Lexeme(<size_t>lexeme)


cdef void string_from_unicode(String* s, unicode uni):
    cdef Py_UNICODE* c_uni = <Py_UNICODE*>uni
    string_from_slice(s, c_uni, 0, len(uni))


cdef inline void string_from_slice(String* s, Py_UNICODE* chars, size_t start, size_t end) nogil:
    s.chars = &chars[start]
    s.n = end - start
    s.key = hash64(s.chars, s.n * sizeof(Py_UNICODE), 0)


cdef inline void string_slice_prefix(String* s, String* prefix, size_t n) nogil:
    string_from_slice(prefix, s.chars, 0, n)
    s.chars += n
    s.n -= n
    s.key = hash64(s.chars, s.n * sizeof(Py_UNICODE), 0)


cdef inline void string_slice_suffix(String* s, String* suffix, size_t n) nogil:
    string_from_slice(suffix, s.chars, s.n - n, s.n)
    s.n -= n
    s.key = hash64(s.chars, s.n * sizeof(Py_UNICODE), 0)
