# cython: embedsignature=True
from __future__ import unicode_literals

from os import path
import re

from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as preinc

from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap

from .structs cimport UniStr
from .strings cimport slice_unicode
from .morphology cimport set_morph_from_dict

from . import util
from .util import read_lang_data
from .tokens import Tokens


cdef class Tokenizer:
    def __init__(self, Vocab vocab, rules, prefix_re, suffix_re, infix_re,
                 pos_tags, tag_names):
        self.mem = Pool()
        self._cache = PreshMap()
        self._specials = PreshMap()
        self._prefix_re = prefix_re
        self._suffix_re = suffix_re
        self._infix_re = infix_re
        self.vocab = vocab
        self._load_special_tokenization(rules, pos_tags, tag_names)

    cpdef Tokens tokens_from_list(self, list strings):
        cdef int length = sum([len(s) for s in strings])
        cdef Tokens tokens = Tokens(self.vocab, ' '.join(strings))
        if length == 0:
            return tokens
        cdef UniStr string_struct
        cdef unicode py_string
        cdef int idx = 0
        for i, py_string in enumerate(strings):
            slice_unicode(&string_struct, py_string, 0, len(py_string))
            tokens.push_back(idx, <const LexemeC*>self.vocab.get(tokens.mem, &string_struct))
            idx += len(py_string) + 1
        return tokens

    def __call__(self, unicode string):
        """Tokenize a string.

        The tokenization rules are defined in three places:

        * The data/<lang>/tokenization table, which handles special cases like contractions;
        * The data/<lang>/prefix file, used to build a regex to split off prefixes;
        * The data/<lang>/suffix file, used to build a regex to split off suffixes.

        The string is first split on whitespace.  To tokenize a whitespace-delimited
        chunk, we first try to look it up in the special-cases. If it's not found,
        we split off a prefix, and then try again. If it's still not found, we
        split off a suffix, and repeat.

        Args:
            string (unicode): The string to be tokenized.

        Returns:
            tokens (Tokens): A Tokens object, giving access to a sequence of LexemeCs.
        """
        cdef int length = len(string)
        cdef Tokens tokens = Tokens(self.vocab, string)
        if length == 0:
            return tokens
        cdef int i = 0
        cdef int start = 0
        cdef bint cache_hit
        cdef Py_UNICODE* chars = string
        cdef bint in_ws = Py_UNICODE_ISSPACE(chars[0])
        cdef UniStr span
        for i in range(1, length):
            # TODO: Allow control of hyphenation
            if (Py_UNICODE_ISSPACE(chars[i]) or chars[i] == '-') != in_ws:
            #if Py_UNICODE_ISSPACE(chars[i]) != in_ws:
                if start < i:
                    slice_unicode(&span, chars, start, i)
                    cache_hit = self._try_cache(start, span.key, tokens)
                    if not cache_hit:
                        self._tokenize(tokens, &span, start, i)
                in_ws = not in_ws
                start = i
                if chars[i] == ' ':
                    start += 1
        i += 1
        if start < i:
            slice_unicode(&span, chars, start, i)
            cache_hit = self._try_cache(start, span.key, tokens)
            if not cache_hit:
                self._tokenize(tokens, &span, start, i)
        return tokens

    cdef int _try_cache(self, int idx, hash_t key, Tokens tokens) except -1:
        cached = <_Cached*>self._cache.get(key)
        if cached == NULL:
            return False
        cdef int i
        if cached.is_lex:
            for i in range(cached.length):
                idx = tokens.push_back(idx, cached.data.lexemes[i])
        else:
            for i in range(cached.length):
                idx = tokens.push_back(idx, &cached.data.tokens[i])
        return True

    cdef int _tokenize(self, Tokens tokens, UniStr* span, int start, int end) except -1:
        cdef vector[LexemeC*] prefixes
        cdef vector[LexemeC*] suffixes
        cdef hash_t orig_key
        cdef int orig_size
        orig_key = span.key
        orig_size = tokens.length
        self._split_affixes(span, &prefixes, &suffixes)
        self._attach_tokens(tokens, start, span, &prefixes, &suffixes)
        self._save_cached(&tokens.data[orig_size], orig_key, tokens.length - orig_size)

    cdef UniStr* _split_affixes(self, UniStr* string, vector[const LexemeC*] *prefixes,
                                vector[const LexemeC*] *suffixes) except NULL:
        cdef size_t i
        cdef UniStr prefix
        cdef UniStr suffix
        cdef UniStr minus_pre
        cdef UniStr minus_suf
        cdef size_t last_size = 0
        while string.n != 0 and string.n != last_size:
            last_size = string.n
            pre_len = self._find_prefix(string.chars, string.n)
            if pre_len != 0:
                slice_unicode(&prefix, string.chars, 0, pre_len)
                slice_unicode(&minus_pre, string.chars, pre_len, string.n)
                # Check whether we've hit a special-case
                if minus_pre.n >= 1 and self._specials.get(minus_pre.key) != NULL:
                    string[0] = minus_pre
                    prefixes.push_back(self.vocab.get(self.vocab.mem, &prefix))
                    break
            suf_len = self._find_suffix(string.chars, string.n)
            if suf_len != 0:
                slice_unicode(&suffix, string.chars, string.n - suf_len, string.n)
                slice_unicode(&minus_suf, string.chars, 0, string.n - suf_len)
                # Check whether we've hit a special-case
                if minus_suf.n >= 1 and self._specials.get(minus_suf.key) != NULL:
                    string[0] = minus_suf
                    suffixes.push_back(self.vocab.get(self.vocab.mem, &suffix))
                    break
            if pre_len and suf_len and (pre_len + suf_len) <= string.n:
                slice_unicode(string, string.chars, pre_len, string.n - suf_len)
                prefixes.push_back(self.vocab.get(self.vocab.mem, &prefix))
                suffixes.push_back(self.vocab.get(self.vocab.mem, &suffix))
            elif pre_len:
                string[0] = minus_pre
                prefixes.push_back(self.vocab.get(self.vocab.mem, &prefix))
            elif suf_len:
                string[0] = minus_suf
                suffixes.push_back(self.vocab.get(self.vocab.mem, &suffix))
            if self._specials.get(string.key):
                break
        return string

    cdef int _attach_tokens(self, Tokens tokens, int idx, UniStr* string,
                            vector[const LexemeC*] *prefixes,
                            vector[const LexemeC*] *suffixes) except -1:
        cdef bint cache_hit
        cdef int split
        cdef const LexemeC* const* lexemes
        cdef LexemeC* lexeme
        cdef UniStr span
        cdef int i
        if prefixes.size():
            for i in range(prefixes.size()):
                idx = tokens.push_back(idx, prefixes[0][i])
        if string.n != 0:
            cache_hit = self._try_cache(idx, string.key, tokens)
            if cache_hit:
                # Get last idx
                idx = tokens.data[tokens.length - 1].idx
                # Increment by last length
                idx += tokens.data[tokens.length - 1].lex.length
            else:
                split = self._find_infix(string.chars, string.n)
                if split == 0 or split == -1:
                    idx = tokens.push_back(idx, self.vocab.get(tokens.mem, string))
                else:
                    slice_unicode(&span, string.chars, 0, split)
                    idx = tokens.push_back(idx, self.vocab.get(tokens.mem, &span))
                    slice_unicode(&span, string.chars, split, split+1)
                    idx = tokens.push_back(idx, self.vocab.get(tokens.mem, &span))
                    slice_unicode(&span, string.chars, split + 1, string.n)
                    idx = tokens.push_back(idx, self.vocab.get(tokens.mem, &span))
        cdef vector[const LexemeC*].reverse_iterator it = suffixes.rbegin()
        while it != suffixes.rend():
            idx = tokens.push_back(idx, deref(it))
            preinc(it)

    cdef int _save_cached(self, const TokenC* tokens, hash_t key, int n) except -1:
        cdef int i
        for i in range(n):
            if tokens[i].lex.id == 1:
                return 0
        cached = <_Cached*>self.mem.alloc(1, sizeof(_Cached))
        cached.length = n
        cached.is_lex = True
        lexemes = <const LexemeC**>self.mem.alloc(n, sizeof(LexemeC**))
        for i in range(n):
            lexemes[i] = tokens[i].lex
        cached.data.lexemes = <const LexemeC* const*>lexemes
        self._cache.set(key, cached)

    cdef int _find_infix(self, Py_UNICODE* chars, size_t length) except -1:
        cdef unicode string = chars[:length]
        match = self._infix_re.search(string)
        return match.start() if match is not None else 0

    cdef int _find_prefix(self, Py_UNICODE* chars, size_t length) except -1:
        cdef unicode string = chars[:length]
        match = self._prefix_re.search(string)
        return (match.end() - match.start()) if match is not None else 0

    cdef int _find_suffix(self, Py_UNICODE* chars, size_t length) except -1:
        cdef unicode string = chars[:length]
        match = self._suffix_re.search(string)
        return (match.end() - match.start()) if match is not None else 0

    def _load_special_tokenization(self, object rules, object tag_map, object tag_names):
        '''Add a special-case tokenization rule.
        '''
        cdef int i
        cdef unicode chunk
        cdef list substrings
        cdef unicode form
        cdef unicode lemma
        cdef dict props
        cdef LexemeC** lexemes
        cdef hash_t hashed
        cdef UniStr string
        for chunk, substrings in sorted(rules.items()):
            tokens = <TokenC*>self.mem.alloc(len(substrings) + 1, sizeof(TokenC))
            for i, props in enumerate(substrings):
                form = props['F']
                lemma = props.get("L", None)
                slice_unicode(&string, form, 0, len(form))
                tokens[i].lex = <LexemeC*>self.vocab.get(self.vocab.mem, &string)
                if lemma is not None:
                    tokens[i].lemma = self.vocab.strings[lemma]
                else:
                    tokens[i].lemma = 0
                if 'pos' in props:
                    # TODO: Clean up this mess...
                    tokens[i].tag = self.vocab.strings[props['pos']]
                    tokens[i].pos = tag_map[props['pos']][0]
                    # These are defaults, which can be over-ridden by the
                    # token-specific props.
                    set_morph_from_dict(&tokens[i].morph, tag_map[props['pos']][1])
                    if tokens[i].lemma == 0:
                        tokens[i].lemma = tokens[i].lex.orth
                set_morph_from_dict(&tokens[i].morph, props)
            cached = <_Cached*>self.mem.alloc(1, sizeof(_Cached))
            cached.length = len(substrings)
            cached.is_lex = False
            cached.data.tokens = tokens
            slice_unicode(&string, chunk, 0, len(chunk))
            self._specials.set(string.key, cached)
            self._cache.set(string.key, cached)
