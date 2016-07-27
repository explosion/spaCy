# cython: embedsignature=True
from __future__ import unicode_literals

from os import path
import re

from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as preinc
from cpython cimport Py_UNICODE_ISSPACE

from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap

from .strings cimport hash_string
cimport cython

from . import util
from .tokens.doc cimport Doc
from .util import read_lang_data, get_package


cdef class Tokenizer:
    def __init__(self, Vocab vocab, rules, prefix_re, suffix_re, infix_re):
        self.mem = Pool()
        self._cache = PreshMap()
        self._specials = PreshMap()
        self._prefix_re = prefix_re
        self._suffix_re = suffix_re
        self._infix_re = infix_re
        self.vocab = vocab
        self._rules = {}
        for chunk, substrings in sorted(rules.items()):
            self.add_special_case(chunk, substrings)

    def __reduce__(self):
        args = (self.vocab, 
                self._rules, 
                self._prefix_re, 
                self._suffix_re, 
                self._infix_re)

        return (self.__class__, args, None, None)

    @classmethod
    def load(cls, data_dir, Vocab vocab):
        return cls.from_package(get_package(data_dir), vocab=vocab)

    @classmethod
    def from_package(cls, package, Vocab vocab):
        rules, prefix_re, suffix_re, infix_re = read_lang_data(package)
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
        if len(string) >= (2 ** 30):
            raise ValueError(
                "String is too long: %d characters. Max is 2**30." % len(string)
            )
        cdef int length = len(string)
        cdef Doc tokens = Doc(self.vocab)
        if length == 0:
            return tokens
        cdef int i = 0
        cdef int start = 0
        cdef bint cache_hit
        cdef bint in_ws = string[0].isspace()
        cdef unicode span
        # The task here is much like string.split, but not quite
        # We find spans of whitespace and non-space characters, and ignore
        # spans that are exactly ' '. So, our sequences will all be separated
        # by either ' ' or nothing.
        for uc in string:
            if uc.isspace() != in_ws:
                if start < i:
                    # When we want to make this fast, get the data buffer once
                    # with PyUnicode_AS_DATA, and then maintain a start_byte
                    # and end_byte, so we can call hash64 directly. That way
                    # we don't have to create the slice when we hit the cache.
                    span = string[start:i]
                    key = hash_string(span)
                    cache_hit = self._try_cache(key, tokens)
                    if not cache_hit:
                        self._tokenize(tokens, span, key)
                if uc == ' ':
                    tokens.c[tokens.length - 1].spacy = True
                    start = i + 1
                else:
                    start = i
                in_ws = not in_ws
            i += 1
        i += 1
        if start < i:
            span = string[start:]
            key = hash_string(span)
            cache_hit = self._try_cache(key, tokens)
            if not cache_hit:
                self._tokenize(tokens, span, key)
            tokens.c[tokens.length - 1].spacy = string[-1] == ' ' and not in_ws
        return tokens

    def pipe(self, texts, batch_size=1000, n_threads=2):
        for text in texts:
            yield self(text)

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
        span = self._split_affixes(tokens.mem, span, &prefixes, &suffixes)
        self._attach_tokens(tokens, span, &prefixes, &suffixes)
        self._save_cached(&tokens.c[orig_size], orig_key, tokens.length - orig_size)

    cdef unicode _split_affixes(self, Pool mem, unicode string,
                                vector[const LexemeC*] *prefixes,
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
                    prefixes.push_back(self.vocab.get(mem, prefix))
                    break
            suf_len = self.find_suffix(string)
            if suf_len != 0:
                suffix = string[-suf_len:]
                minus_suf = string[:-suf_len]
                # Check whether we've hit a special-case
                if minus_suf and (self._specials.get(hash_string(minus_suf)) != NULL):
                    string = minus_suf
                    suffixes.push_back(self.vocab.get(mem, suffix))
                    break
            if pre_len and suf_len and (pre_len + suf_len) <= len(string):
                string = string[pre_len:-suf_len]
                prefixes.push_back(self.vocab.get(mem, prefix))
                suffixes.push_back(self.vocab.get(mem, suffix))
            elif pre_len:
                string = minus_pre
                prefixes.push_back(self.vocab.get(mem, prefix))
            elif suf_len:
                string = minus_suf
                suffixes.push_back(self.vocab.get(mem, suffix))
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
            if not cache_hit:
                matches = self.find_infix(string)
                if not matches:
                    tokens.push_back(self.vocab.get(tokens.mem, string), False)
                else:
                    # let's say we have dyn-o-mite-dave
                    # the regex finds the start and end positions of the hyphens
                    start = 0
                    for match in matches:
                        infix_start = match.start()
                        infix_end = match.end()
                        if infix_start == start:
                            continue
                        span = string[start:infix_start]
                        tokens.push_back(self.vocab.get(tokens.mem, span), False)
                    
                        infix_span = string[infix_start:infix_end]
                        tokens.push_back(self.vocab.get(tokens.mem, infix_span), False)
                        start = infix_end
                    span = string[start:]
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
        return list(self._infix_re.finditer(string))

    def find_prefix(self, unicode string):
        match = self._prefix_re.search(string)
        return (match.end() - match.start()) if match is not None else 0

    def find_suffix(self, unicode string):
        match = self._suffix_re.search(string)
        return (match.end() - match.start()) if match is not None else 0

    def _load_special_tokenization(self, special_cases):
        '''Add special-case tokenization rules.
        '''
        for chunk, substrings in sorted(special_cases.items()):
            self.add_special_case(chunk, substrings)
    
    def add_special_case(self, unicode chunk, substrings):
        '''Add a special-case tokenization rule.

        For instance, "don't" is special-cased to tokenize into
        ["do", "n't"]. The split tokens can have lemmas and part-of-speech
        tags.
        '''
        substrings = list(substrings)
        cached = <_Cached*>self.mem.alloc(1, sizeof(_Cached))
        cached.length = len(substrings)
        cached.is_lex = False
        cached.data.tokens = self.vocab.make_fused_token(substrings)
        key = hash_string(chunk)
        self._specials.set(key, cached)
        self._cache.set(key, cached)
        self._rules[chunk] = substrings
