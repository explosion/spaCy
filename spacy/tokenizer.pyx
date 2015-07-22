# cython: embedsignature=True
from __future__ import unicode_literals

from os import path
import re

from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as preinc
from cpython cimport Py_UNICODE_ISSPACE

from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap
from murmurhash.mrmr cimport hash64

from .morphology cimport set_morph_from_dict
from .strings cimport hash_string
cimport cython

from . import util
from .util import read_lang_data
from .tokens.doc cimport Doc


cdef class Tokenizer:
    def __init__(self, Vocab vocab, rules, prefix_re, suffix_re, infix_re):
        self.mem = Pool()
        self._cache = PreshMap()
        self._specials = PreshMap()
        self._prefix_re = prefix_re
        self._suffix_re = suffix_re
        self._infix_re = infix_re
        self.vocab = vocab
        self._load_special_tokenization(rules, self.vocab.pos_tags)

    @classmethod
    def from_dir(cls, Vocab vocab, data_dir):
        rules, prefix_re, suffix_re, infix_re = read_lang_data(data_dir)
        prefix_re = re.compile(prefix_re)
        suffix_re = re.compile(suffix_re)
        infix_re = re.compile(infix_re)
        return cls(vocab, rules, prefix_re, suffix_re, infix_re)

    cpdef Doc tokens_from_list(self, list strings):
        cdef Doc tokens = Doc(self.vocab)
        if sum([len(s) for s in strings]) == 0:
            return tokens
        cdef unicode py_string
        cdef int idx = 0
        for i, py_string in enumerate(strings):
            # Note that we pass tokens.mem here --- the Doc object has ownership
            tokens.push_back(
                <const LexemeC*>self.vocab.get(tokens.mem, py_string), True)
            idx += len(py_string) + 1
        return tokens

    @cython.boundscheck(False)
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
            tokens (Doc): A Doc object, giving access to a sequence of LexemeCs.
        """
        cdef int length = len(string)
        cdef Doc tokens = Doc(self.vocab)
        if length == 0:
            return tokens
        cdef int i = 0
        cdef int start = 0
        cdef bint cache_hit
        cdef bint in_ws = Py_UNICODE_ISSPACE(string[0])
        cdef unicode span
        # Use of Py_UNICODE is deprecated, and I should be using Py_UCS4.
        # But this is hard --- I need to acquire a pointer, but there's no
        # Py_UCS4 API in Python 2.
        cdef Py_UNICODE uc
        cdef Py_UNICODE* chars_ptr = <Py_UNICODE*>string
        # The task here is much like string.split, but not quite
        # We find spans of whitespace and non-space characters, and ignore
        # spans that are exactly ' '. So, our sequences will all be separated
        # by either ' ' or nothing.
        for i in range(1, length):
            uc = chars_ptr[i]
            if Py_UNICODE_ISSPACE(uc) != in_ws:
                if start < i:
                    key = hash64(&chars_ptr[start], (i - start) * sizeof(Py_UNICODE), 0)
                    cache_hit = self._try_cache(key, tokens)
                    if not cache_hit:
                        self._tokenize(tokens, string[start:i], key)
                in_ws = not in_ws
                if uc == ' ':
                    tokens.data[tokens.length - 1].spacy = True
                    start = i + 1
                else:
                    start = i
        i += 1
        if start < i:
            key = hash64(&chars_ptr[start], (i - start) * sizeof(Py_UNICODE), 0)
            cache_hit = self._try_cache(key, tokens)
            if not cache_hit:
                self._tokenize(tokens, string[start:], key)
            tokens.data[tokens.length - 1].spacy = string[-1] == ' '
        return tokens

    cdef int _try_cache(self, hash_t key, Doc tokens) except -1:
        cached = <_Cached*>self._cache.get(key)
        if cached == NULL:
            return False
        cdef int i
        if cached.is_lex:
            for i in range(cached.length):
                tokens.push_back(cached.data.lexemes[i], False)
        else:
            for i in range(cached.length):
                tokens.push_back(&cached.data.tokens[i], False)
        return True

    cdef int _tokenize(self, Doc tokens, unicode span, hash_t orig_key) except -1:
        cdef vector[LexemeC*] prefixes
        cdef vector[LexemeC*] suffixes
        cdef int orig_size
        orig_size = tokens.length
        span = self._split_affixes(span, &prefixes, &suffixes)
        self._attach_tokens(tokens, span, &prefixes, &suffixes)
        self._save_cached(&tokens.data[orig_size], orig_key, tokens.length - orig_size)

    cdef unicode _split_affixes(self, unicode string, vector[const LexemeC*] *prefixes,
                                vector[const LexemeC*] *suffixes):
        cdef size_t i
        cdef unicode prefix
        cdef unicode suffix
        cdef unicode minus_pre
        cdef unicode minus_suf
        cdef size_t last_size = 0
        while string and len(string) != last_size:
            last_size = len(string)
            pre_len = self.find_prefix(string)
            if pre_len != 0:
                prefix = string[:pre_len]
                minus_pre = string[pre_len:]
                # Check whether we've hit a special-case
                if minus_pre and self._specials.get(hash_string(minus_pre)) != NULL:
                    string = minus_pre
                    prefixes.push_back(self.vocab.get(self.vocab.mem, prefix))
                    break
            suf_len = self.find_suffix(string)
            if suf_len != 0:
                suffix = string[-suf_len:]
                minus_suf = string[:-suf_len]
                # Check whether we've hit a special-case
                if minus_suf and (self._specials.get(hash_string(minus_suf)) != NULL):
                    string = minus_suf
                    suffixes.push_back(self.vocab.get(self.vocab.mem, suffix))
                    break
            if pre_len and suf_len and (pre_len + suf_len) <= len(string):
                string = string[pre_len:-suf_len]
                prefixes.push_back(self.vocab.get(self.vocab.mem, prefix))
                suffixes.push_back(self.vocab.get(self.vocab.mem, suffix))
            elif pre_len:
                string = minus_pre
                prefixes.push_back(self.vocab.get(self.vocab.mem, prefix))
            elif suf_len:
                string = minus_suf
                suffixes.push_back(self.vocab.get(self.vocab.mem, suffix))
            if string and (self._specials.get(hash_string(string)) != NULL):
                break
        return string

    cdef int _attach_tokens(self, Doc tokens, unicode string,
                            vector[const LexemeC*] *prefixes,
                            vector[const LexemeC*] *suffixes) except -1:
        cdef bint cache_hit
        cdef int split, end
        cdef const LexemeC* const* lexemes
        cdef const LexemeC* lexeme
        cdef unicode span
        cdef int i
        if prefixes.size():
            for i in range(prefixes.size()):
                tokens.push_back(prefixes[0][i], False)
        if string:
            cache_hit = self._try_cache(hash_string(string), tokens)
            if cache_hit:
                pass
            else:
                match = self.find_infix(string)
                if match is None:
                    tokens.push_back(self.vocab.get(tokens.mem, string), False)
                else:
                    split = match.start()
                    end = match.end()
                    # Append the beginning, affix, end of the infix span
                    span = string[:split]
                    tokens.push_back(self.vocab.get(tokens.mem, span), False)
                    
                    span = string[split:end]
                    tokens.push_back(self.vocab.get(tokens.mem, span), False)
                    
                    span = string[end:]
                    tokens.push_back(self.vocab.get(tokens.mem, span), False)
        cdef vector[const LexemeC*].reverse_iterator it = suffixes.rbegin()
        while it != suffixes.rend():
            lexeme = deref(it)
            preinc(it)
            tokens.push_back(lexeme, False)

    cdef int _save_cached(self, const TokenC* tokens, hash_t key, int n) except -1:
        cdef int i
        for i in range(n):
            if tokens[i].lex.id == 0:
                return 0
        cached = <_Cached*>self.mem.alloc(1, sizeof(_Cached))
        cached.length = n
        cached.is_lex = True
        lexemes = <const LexemeC**>self.mem.alloc(n, sizeof(LexemeC**))
        for i in range(n):
            lexemes[i] = tokens[i].lex
        cached.data.lexemes = <const LexemeC* const*>lexemes
        self._cache.set(key, cached)

    def find_infix(self, unicode string):
        return self._infix_re.search(string)

    def find_prefix(self, unicode string):
        match = self._prefix_re.search(string)
        return (match.end() - match.start()) if match is not None else 0

    def find_suffix(self, unicode string):
        match = self._suffix_re.search(string)
        return (match.end() - match.start()) if match is not None else 0

    def _load_special_tokenization(self, object rules, object tag_map):
        '''Add a special-case tokenization rule.
        '''
        cdef int i
        cdef list substrings
        cdef unicode chunk
        cdef unicode form
        cdef unicode lemma
        cdef dict props
        cdef LexemeC** lexemes
        cdef hash_t hashed
        for chunk, substrings in sorted(rules.items()):
            tokens = <TokenC*>self.mem.alloc(len(substrings) + 1, sizeof(TokenC))
            for i, props in enumerate(substrings):
                form = props['F']
                lemma = props.get("L", None)
                tokens[i].lex = <LexemeC*>self.vocab.get(self.vocab.mem, form)
                if lemma is not None:
                    tokens[i].lemma = self.vocab.strings[lemma]
                else:
                    tokens[i].lemma = 0
                if 'pos' in props:
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
            hashed = hash_string(chunk)
            self._specials.set(hashed, cached)
            self._cache.set(hashed, cached)
