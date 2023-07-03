# cython: embedsignature=True, profile=True, binding=True
cimport cython
from cymem.cymem cimport Pool
from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as preinc
from libc.string cimport memcpy, memset
from libcpp.set cimport set as stdset
from preshed.maps cimport PreshMap

import re
import warnings

from .lexeme cimport EMPTY_LEXEME
from .strings cimport hash_string
from .tokens.doc cimport Doc

from . import util
from .attrs import intify_attrs
from .errors import Errors, Warnings
from .scorer import Scorer
from .symbols import NORM, ORTH
from .tokens import Span
from .training import validate_examples
from .util import get_words_and_spaces, registry


cdef class Tokenizer:
    """Segment text, and create Doc objects with the discovered segment
    boundaries.

    DOCS: https://spacy.io/api/tokenizer
    """
    def __init__(self, Vocab vocab, rules=None, prefix_search=None,
                 suffix_search=None, infix_finditer=None, token_match=None,
                 url_match=None, faster_heuristics=True):
        """Create a `Tokenizer`, to create `Doc` objects given unicode text.

        vocab (Vocab): A storage container for lexical types.
        rules (dict): Exceptions and special-cases for the tokenizer.
        prefix_search (callable): A function matching the signature of
            `re.compile(string).search` to match prefixes.
        suffix_search (callable): A function matching the signature of
            `re.compile(string).search` to match suffixes.
        infix_finditer (callable): A function matching the signature of
            `re.compile(string).finditer` to find infixes.
        token_match (callable): A function matching the signature of
            `re.compile(string).match`, for matching strings to be
            recognized as tokens.
        url_match (callable): A function matching the signature of
            `re.compile(string).match`, for matching strings to be
            recognized as urls.
        faster_heuristics (bool): Whether to restrict the final
            Matcher-based pass for rules to those containing affixes or space.
            Defaults to True.

        EXAMPLE:
            >>> tokenizer = Tokenizer(nlp.vocab)

        DOCS: https://spacy.io/api/tokenizer#init
        """
        self.mem = Pool()
        self._cache = PreshMap()
        self._specials = PreshMap()
        self.token_match = token_match
        self.url_match = url_match
        self.prefix_search = prefix_search
        self.suffix_search = suffix_search
        self.infix_finditer = infix_finditer
        self.vocab = vocab
        self.faster_heuristics = faster_heuristics
        self._rules = {}
        self._special_matcher = PhraseMatcher(self.vocab)
        self._load_special_cases(rules)

    property token_match:
        def __get__(self):
            return self._token_match

        def __set__(self, token_match):
            self._token_match = token_match
            self._reload_special_cases()

    property url_match:
        def __get__(self):
            return self._url_match

        def __set__(self, url_match):
            self._url_match = url_match
            self._reload_special_cases()

    property prefix_search:
        def __get__(self):
            return self._prefix_search

        def __set__(self, prefix_search):
            self._prefix_search = prefix_search
            self._reload_special_cases()

    property suffix_search:
        def __get__(self):
            return self._suffix_search

        def __set__(self, suffix_search):
            self._suffix_search = suffix_search
            self._reload_special_cases()

    property infix_finditer:
        def __get__(self):
            return self._infix_finditer

        def __set__(self, infix_finditer):
            self._infix_finditer = infix_finditer
            self._reload_special_cases()

    property rules:
        def __get__(self):
            return self._rules

        def __set__(self, rules):
            self._rules = {}
            self._flush_cache()
            self._flush_specials()
            self._cache = PreshMap()
            self._specials = PreshMap()
            self._load_special_cases(rules)

    property faster_heuristics:
        def __get__(self):
            return bool(self._faster_heuristics)

        def __set__(self, faster_heuristics):
            self._faster_heuristics = bool(faster_heuristics)
            self._reload_special_cases()

    def __reduce__(self):
        args = (self.vocab,
                self.rules,
                self.prefix_search,
                self.suffix_search,
                self.infix_finditer,
                self.token_match,
                self.url_match)
        return (self.__class__, args, None, None)

    def __call__(self, str string):
        """Tokenize a string.

        string (str): The string to tokenize.
        RETURNS (Doc): A container for linguistic annotations.

        DOCS: https://spacy.io/api/tokenizer#call
        """
        doc = self._tokenize_affixes(string, True)
        self._apply_special_cases(doc)
        return doc

    @cython.boundscheck(False)
    cdef Doc _tokenize_affixes(self, str string, bint with_special_cases):
        """Tokenize according to affix and token_match settings.

        string (str): The string to tokenize.
        RETURNS (Doc): A container for linguistic annotations.
        """
        if len(string) >= (2 ** 30):
            raise ValueError(Errors.E025.format(length=len(string)))
        cdef int length = len(string)
        cdef Doc doc = Doc(self.vocab)
        if length == 0:
            return doc
        cdef int i = 0
        cdef int start = 0
        cdef int has_special = 0
        cdef bint in_ws = string[0].isspace()
        cdef str span
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
                    if not self._try_specials_and_cache(key, doc, &has_special, with_special_cases):
                        self._tokenize(doc, span, key, &has_special, with_special_cases)
                if uc == ' ':
                    doc.c[doc.length - 1].spacy = True
                    start = i + 1
                else:
                    start = i
                in_ws = not in_ws
            i += 1
        if start < i:
            span = string[start:]
            key = hash_string(span)
            if not self._try_specials_and_cache(key, doc, &has_special, with_special_cases):
                self._tokenize(doc, span, key, &has_special, with_special_cases)
            doc.c[doc.length - 1].spacy = string[-1] == " " and not in_ws
        return doc

    def pipe(self, texts, batch_size=1000):
        """Tokenize a stream of texts.

        texts: A sequence of unicode texts.
        batch_size (int): Number of texts to accumulate in an internal buffer.
        Defaults to 1000.
        YIELDS (Doc): A sequence of Doc objects, in order.

        DOCS: https://spacy.io/api/tokenizer#pipe
        """
        for text in texts:
            yield self(text)

    def _flush_cache(self):
        self._reset_cache([key for key in self._cache])

    def _reset_cache(self, keys):
        for k in keys:
            cached = <_Cached*>self._cache.get(k)
            del self._cache[k]
            if cached is not NULL:
                self.mem.free(cached)

    def _flush_specials(self):
        self._special_matcher = PhraseMatcher(self.vocab)
        for k in self._specials:
            cached = <_Cached*>self._specials.get(k)
            del self._specials[k]
            if cached is not NULL:
                self.mem.free(cached)

    cdef int _apply_special_cases(self, Doc doc) except -1:
        """Retokenize doc according to special cases.

        doc (Doc): Document.
        """
        cdef int i
        cdef int max_length = 0
        cdef bint modify_in_place
        cdef Pool mem = Pool()
        cdef vector[SpanC] c_matches
        cdef vector[SpanC] c_filtered
        cdef int offset
        cdef int modified_doc_length
        # Find matches for special cases
        self._special_matcher.find_matches(doc, 0, doc.length, &c_matches)
        # Skip processing if no matches
        if c_matches.size() == 0:
            return True
        self._filter_special_spans(c_matches, c_filtered, doc.length)
        # Put span info in span.start-indexed dict and calculate maximum
        # intermediate document size
        (span_data, max_length, modify_in_place) = self._prepare_special_spans(doc, c_filtered)
        # If modifications never increase doc length, can modify in place
        if modify_in_place:
            tokens = doc.c
        # Otherwise create a separate array to store modified tokens
        else:
            assert max_length > 0
            tokens = <TokenC*>mem.alloc(max_length, sizeof(TokenC))
        # Modify tokenization according to filtered special cases
        offset = self._retokenize_special_spans(doc, tokens, span_data)
        # Allocate more memory for doc if needed
        modified_doc_length = doc.length + offset
        while modified_doc_length >= doc.max_length:
            doc._realloc(doc.max_length * 2)
        # If not modified in place, copy tokens back to doc
        if not modify_in_place:
            memcpy(doc.c, tokens, max_length * sizeof(TokenC))
        for i in range(doc.length + offset, doc.length):
            memset(&doc.c[i], 0, sizeof(TokenC))
            doc.c[i].lex = &EMPTY_LEXEME
        doc.length = doc.length + offset
        return True

    cdef void _filter_special_spans(self, vector[SpanC] &original, vector[SpanC] &filtered, int doc_len) nogil:

        cdef int seen_i
        cdef SpanC span
        cdef stdset[int] seen_tokens
        stdsort(original.begin(), original.end(), len_start_cmp)
        cdef int orig_i = original.size() - 1
        while orig_i >= 0:
            span = original[orig_i]
            if not seen_tokens.count(span.start) and not seen_tokens.count(span.end - 1):
                filtered.push_back(span)
            for seen_i in range(span.start, span.end):
                seen_tokens.insert(seen_i)
            orig_i -= 1
        stdsort(filtered.begin(), filtered.end(), start_cmp)

    cdef object _prepare_special_spans(self, Doc doc, vector[SpanC] &filtered):
        spans = [doc[match.start:match.end] for match in filtered]
        cdef bint modify_in_place = True
        cdef int curr_length = doc.length
        cdef int max_length = 0
        cdef int span_length_diff = 0
        span_data = {}
        for span in spans:
            rule = self._rules.get(span.text, None)
            span_length_diff = 0
            if rule:
                span_length_diff = len(rule) - (span.end - span.start)
            if span_length_diff > 0:
                modify_in_place = False
            curr_length += span_length_diff
            if curr_length > max_length:
                max_length = curr_length
            span_data[span.start] = (span.text, span.start, span.end, span_length_diff)
        return (span_data, max_length, modify_in_place)

    cdef int _retokenize_special_spans(self, Doc doc, TokenC* tokens, object span_data):
        cdef int i = 0
        cdef int j = 0
        cdef int offset = 0
        cdef _Cached* cached
        cdef int idx_offset = 0
        cdef int orig_final_spacy
        cdef int orig_idx
        cdef int span_start
        cdef int span_end
        while i < doc.length:
            if not i in span_data:
                tokens[i + offset] = doc.c[i]
                i += 1
            else:
                span = span_data[i]
                span_start = span[1]
                span_end = span[2]
                cached = <_Cached*>self._specials.get(hash_string(span[0]))
                if cached == NULL:
                    # Copy original tokens if no rule found
                    for j in range(span_end - span_start):
                        tokens[i + offset + j] = doc.c[i + j]
                    i += span_end - span_start
                else:
                    # Copy special case tokens into doc and adjust token and
                    # character offsets
                    idx_offset = 0
                    orig_final_spacy = doc.c[span_end - 1].spacy
                    orig_idx = doc.c[i].idx
                    for j in range(cached.length):
                        tokens[i + offset + j] = cached.data.tokens[j]
                        tokens[i + offset + j].idx = orig_idx + idx_offset
                        idx_offset += cached.data.tokens[j].lex.length
                        if cached.data.tokens[j].spacy:
                            idx_offset += 1
                    tokens[i + offset + cached.length - 1].spacy = orig_final_spacy
                    i += span_end - span_start
                    offset += span[3]
        return offset

    cdef int _try_specials_and_cache(self, hash_t key, Doc tokens, int* has_special, bint with_special_cases) except -1:
        cdef bint specials_hit = 0
        cdef bint cache_hit = 0
        cdef int i
        if with_special_cases:
            cached = <_Cached*>self._specials.get(key)
            if cached == NULL:
                specials_hit = False
            else:
                for i in range(cached.length):
                    tokens.push_back(&cached.data.tokens[i], False)
                has_special[0] = 1
                specials_hit = True
        if not specials_hit:
            cached = <_Cached*>self._cache.get(key)
            if cached == NULL:
                cache_hit = False
            else:
                if cached.is_lex:
                    for i in range(cached.length):
                        tokens.push_back(cached.data.lexemes[i], False)
                else:
                    for i in range(cached.length):
                        tokens.push_back(&cached.data.tokens[i], False)
                cache_hit = True
        if not specials_hit and not cache_hit:
            return False
        return True

    cdef int _tokenize(self, Doc tokens, str span, hash_t orig_key, int* has_special, bint with_special_cases) except -1:
        cdef vector[LexemeC*] prefixes
        cdef vector[LexemeC*] suffixes
        cdef int orig_size
        orig_size = tokens.length
        span = self._split_affixes(tokens.mem, span, &prefixes, &suffixes,
                                   has_special, with_special_cases)
        self._attach_tokens(tokens, span, &prefixes, &suffixes, has_special,
                            with_special_cases)
        self._save_cached(&tokens.c[orig_size], orig_key, has_special,
                          tokens.length - orig_size)

    cdef str _split_affixes(self, Pool mem, str string,
                                vector[const LexemeC*] *prefixes,
                                vector[const LexemeC*] *suffixes,
                                int* has_special,
                                bint with_special_cases):
        cdef size_t i
        cdef str prefix
        cdef str suffix
        cdef str minus_pre
        cdef str minus_suf
        cdef size_t last_size = 0
        while string and len(string) != last_size:
            if self.token_match and self.token_match(string):
                break
            if with_special_cases and self._specials.get(hash_string(string)) != NULL:
                break
            last_size = len(string)
            pre_len = self.find_prefix(string)
            if pre_len != 0:
                prefix = string[:pre_len]
                minus_pre = string[pre_len:]
                if minus_pre and with_special_cases and self._specials.get(hash_string(minus_pre)) != NULL:
                    string = minus_pre
                    prefixes.push_back(self.vocab.get(mem, prefix))
                    break
            suf_len = self.find_suffix(string[pre_len:])
            if suf_len != 0:
                suffix = string[-suf_len:]
                minus_suf = string[:-suf_len]
                if minus_suf and with_special_cases and self._specials.get(hash_string(minus_suf)) != NULL:
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
        return string

    cdef int _attach_tokens(self, Doc tokens, str string,
                            vector[const LexemeC*] *prefixes,
                            vector[const LexemeC*] *suffixes,
                            int* has_special,
                            bint with_special_cases) except -1:
        cdef bint specials_hit = 0
        cdef bint cache_hit = 0
        cdef int split, end
        cdef const LexemeC* const* lexemes
        cdef const LexemeC* lexeme
        cdef str span
        cdef int i
        if prefixes.size():
            for i in range(prefixes.size()):
                tokens.push_back(prefixes[0][i], False)
        if string:
            if self._try_specials_and_cache(hash_string(string), tokens, has_special, with_special_cases):
                pass
            elif (self.token_match and self.token_match(string)) or \
                    (self.url_match and \
                    self.url_match(string)):
                # We're always saying 'no' to spaces here -- the caller will
                # fix up the outermost one, with reference to the original.
                # See Issue #859
                tokens.push_back(self.vocab.get(tokens.mem, string), False)
            else:
                matches = self.find_infix(string)
                if not matches:
                    tokens.push_back(self.vocab.get(tokens.mem, string), False)
                else:
                    # Let's say we have dyn-o-mite-dave - the regex finds the
                    # start and end positions of the hyphens
                    start = 0
                    start_before_infixes = start
                    for match in matches:
                        infix_start = match.start()
                        infix_end = match.end()

                        if infix_start == start_before_infixes:
                            continue

                        if infix_start != start:
                            span = string[start:infix_start]
                            tokens.push_back(self.vocab.get(tokens.mem, span), False)

                        if infix_start != infix_end:
                            # If infix_start != infix_end, it means the infix
                            # token is non-empty. Empty infix tokens are useful
                            # for tokenization in some languages (see
                            # https://github.com/explosion/spaCy/issues/768)
                            infix_span = string[infix_start:infix_end]
                            tokens.push_back(self.vocab.get(tokens.mem, infix_span), False)
                        start = infix_end
                    span = string[start:]
                    if span:
                        tokens.push_back(self.vocab.get(tokens.mem, span), False)
        cdef vector[const LexemeC*].reverse_iterator it = suffixes.rbegin()
        while it != suffixes.rend():
            lexeme = deref(it)
            preinc(it)
            tokens.push_back(lexeme, False)

    cdef int _save_cached(self, const TokenC* tokens, hash_t key,
                          int* has_special, int n) except -1:
        cdef int i
        if n <= 0:
            # avoid mem alloc of zero length
            return 0
        for i in range(n):
            if self.vocab._by_orth.get(tokens[i].lex.orth) == NULL:
                return 0
        # See #1250
        if has_special[0]:
            return 0
        cached = <_Cached*>self.mem.alloc(1, sizeof(_Cached))
        cached.length = n
        cached.is_lex = True
        lexemes = <const LexemeC**>self.mem.alloc(n, sizeof(LexemeC**))
        for i in range(n):
            lexemes[i] = tokens[i].lex
        cached.data.lexemes = <const LexemeC* const*>lexemes
        self._cache.set(key, cached)

    def find_infix(self, str string):
        """Find internal split points of the string, such as hyphens.

        string (str): The string to segment.
        RETURNS (list): A list of `re.MatchObject` objects that have `.start()`
            and `.end()` methods, denoting the placement of internal segment
            separators, e.g. hyphens.

        DOCS: https://spacy.io/api/tokenizer#find_infix
        """
        if self.infix_finditer is None:
            return 0
        return list(self.infix_finditer(string))

    def find_prefix(self, str string):
        """Find the length of a prefix that should be segmented from the
        string, or None if no prefix rules match.

        string (str): The string to segment.
        RETURNS (int): The length of the prefix if present, otherwise `None`.

        DOCS: https://spacy.io/api/tokenizer#find_prefix
        """
        if self.prefix_search is None:
            return 0
        match = self.prefix_search(string)
        return (match.end() - match.start()) if match is not None else 0

    def find_suffix(self, str string):
        """Find the length of a suffix that should be segmented from the
        string, or None if no suffix rules match.

        string (str): The string to segment.
        Returns (int): The length of the suffix if present, otherwise `None`.

        DOCS: https://spacy.io/api/tokenizer#find_suffix
        """
        if self.suffix_search is None:
            return 0
        match = self.suffix_search(string)
        return (match.end() - match.start()) if match is not None else 0

    def _load_special_cases(self, special_cases):
        """Add special-case tokenization rules."""
        if special_cases is not None:
            for chunk, substrings in sorted(special_cases.items()):
                self.add_special_case(chunk, substrings)

    def _validate_special_case(self, chunk, substrings):
        """Check whether the `ORTH` fields match the string. Check that
        additional features beyond `ORTH` and `NORM` are not set by the
        exception.

        chunk (str): The string to specially tokenize.
        substrings (iterable): A sequence of dicts, where each dict describes
            a token and its attributes.
        """
        attrs = [intify_attrs(spec, _do_deprecated=True) for spec in substrings]
        orth = "".join([spec[ORTH] for spec in attrs])
        if chunk != orth:
            raise ValueError(Errors.E997.format(chunk=chunk, orth=orth, token_attrs=substrings))
        for substring in attrs:
            for attr in substring:
                if attr not in (ORTH, NORM):
                    raise ValueError(Errors.E1005.format(attr=self.vocab.strings[attr], chunk=chunk))

    def add_special_case(self, str string, substrings):
        """Add a special-case tokenization rule.

        string (str): The string to specially tokenize.
        substrings (iterable): A sequence of dicts, where each dict describes
            a token and its attributes. The `ORTH` fields of the attributes
            must exactly match the string when they are concatenated.

        DOCS: https://spacy.io/api/tokenizer#add_special_case
        """
        self._validate_special_case(string, substrings)
        substrings = list(substrings)
        cached = <_Cached*>self.mem.alloc(1, sizeof(_Cached))
        cached.length = len(substrings)
        cached.is_lex = False
        cached.data.tokens = self.vocab.make_fused_token(substrings)
        key = hash_string(string)
        stale_special = <_Cached*>self._specials.get(key)
        self._specials.set(key, cached)
        if stale_special is not NULL:
            self.mem.free(stale_special)
        self._rules[string] = substrings
        self._flush_cache()
        if not self.faster_heuristics or self.find_prefix(string) or self.find_infix(string) or self.find_suffix(string) or " " in string:
            self._special_matcher.add(string, None, self._tokenize_affixes(string, False))

    def _reload_special_cases(self):
        self._flush_cache()
        self._flush_specials()
        self._load_special_cases(self._rules)

    def explain(self, text):
        """A debugging tokenizer that provides information about which
        tokenizer rule or pattern was matched for each token. The tokens
        produced are identical to `nlp.tokenizer()` except for whitespace
        tokens.

        string (str): The string to tokenize.
        RETURNS (list): A list of (pattern_string, token_string) tuples

        DOCS: https://spacy.io/api/tokenizer#explain
        """
        prefix_search = self.prefix_search
        if prefix_search is None:
            prefix_search = re.compile("a^").search
        suffix_search = self.suffix_search
        if suffix_search is None:
            suffix_search = re.compile("a^").search
        infix_finditer = self.infix_finditer
        if infix_finditer is None:
            infix_finditer = re.compile("a^").finditer
        token_match = self.token_match
        if token_match is None:
            token_match = re.compile("a^").match
        url_match = self.url_match
        if url_match is None:
            url_match = re.compile("a^").match
        special_cases = {}
        for orth, special_tokens in self.rules.items():
            special_cases[orth] = [intify_attrs(special_token, strings_map=self.vocab.strings, _do_deprecated=True) for special_token in special_tokens]
        tokens = []
        for substring in text.split():
            suffixes = []
            while substring:
                if substring in special_cases:
                    tokens.extend(("SPECIAL-" + str(i + 1), self.vocab.strings[e[ORTH]]) for i, e in enumerate(special_cases[substring]))
                    substring = ''
                    continue
                while prefix_search(substring) or suffix_search(substring):
                    if token_match(substring):
                        tokens.append(("TOKEN_MATCH", substring))
                        substring = ''
                        break
                    if substring in special_cases:
                        tokens.extend(("SPECIAL-" + str(i + 1), self.vocab.strings[e[ORTH]]) for i, e in enumerate(special_cases[substring]))
                        substring = ''
                        break
                    if prefix_search(substring):
                        split = prefix_search(substring).end()
                        # break if pattern matches the empty string
                        if split == 0:
                            break
                        tokens.append(("PREFIX", substring[:split]))
                        substring = substring[split:]
                        if substring in special_cases:
                            continue
                    if suffix_search(substring):
                        split = suffix_search(substring).start()
                        # break if pattern matches the empty string
                        if split == len(substring):
                            break
                        suffixes.append(("SUFFIX", substring[split:]))
                        substring = substring[:split]
                if len(substring) == 0:
                    continue
                if token_match(substring):
                    tokens.append(("TOKEN_MATCH", substring))
                    substring = ''
                elif url_match(substring):
                    tokens.append(("URL_MATCH", substring))
                    substring = ''
                elif substring in special_cases:
                    tokens.extend((f"SPECIAL-{i + 1}", self.vocab.strings[e[ORTH]]) for i, e in enumerate(special_cases[substring]))
                    substring = ''
                elif list(infix_finditer(substring)):
                    infixes = infix_finditer(substring)
                    offset = 0
                    for match in infixes:
                        if offset == 0 and match.start() == 0:
                            continue
                        if substring[offset : match.start()]:
                            tokens.append(("TOKEN", substring[offset : match.start()]))
                        if substring[match.start() : match.end()]:
                            tokens.append(("INFIX", substring[match.start() : match.end()]))
                        offset = match.end()
                    if substring[offset:]:
                        tokens.append(("TOKEN", substring[offset:]))
                    substring = ''
                elif substring:
                    tokens.append(("TOKEN", substring))
                    substring = ''
            tokens.extend(reversed(suffixes))
        # Find matches for special cases handled by special matcher
        words, spaces = get_words_and_spaces([t[1] for t in tokens], text)
        t_words = []
        t_spaces = []
        for word, space in zip(words, spaces):
            if not word.isspace():
                t_words.append(word)
                t_spaces.append(space)
        doc = Doc(self.vocab, words=t_words, spaces=t_spaces)
        matches = self._special_matcher(doc)
        spans = [Span(doc, s, e, label=m_id) for m_id, s, e in matches]
        spans = util.filter_spans(spans)
        # Replace matched tokens with their exceptions
        i = 0
        final_tokens = []
        spans_by_start = {s.start: s for s in spans}
        while i < len(tokens):
            if i in spans_by_start:
                span = spans_by_start[i]
                exc = [d[ORTH] for d in special_cases[span.label_]]
                for j, orth in enumerate(exc):
                    final_tokens.append((f"SPECIAL-{j + 1}", self.vocab.strings[orth]))
                i += len(span)
            else:
                final_tokens.append(tokens[i])
                i += 1
        return final_tokens

    def score(self, examples, **kwargs):
        validate_examples(examples, "Tokenizer.score")
        return Scorer.score_tokenization(examples)

    def to_disk(self, path, **kwargs):
        """Save the current state to a directory.

        path (str / Path): A path to a directory, which will be created if
            it doesn't exist.
        exclude (list): String names of serialization fields to exclude.

        DOCS: https://spacy.io/api/tokenizer#to_disk
        """
        path = util.ensure_path(path)
        with path.open("wb") as file_:
            file_.write(self.to_bytes(**kwargs))

    def from_disk(self, path, *, exclude=tuple()):
        """Loads state from a directory. Modifies the object in place and
        returns it.

        path (str / Path): A path to a directory.
        exclude (list): String names of serialization fields to exclude.
        RETURNS (Tokenizer): The modified `Tokenizer` object.

        DOCS: https://spacy.io/api/tokenizer#from_disk
        """
        path = util.ensure_path(path)
        with path.open("rb") as file_:
            bytes_data = file_.read()
        self.from_bytes(bytes_data, exclude=exclude)
        return self

    def to_bytes(self, *, exclude=tuple()):
        """Serialize the current state to a binary string.

        exclude (list): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized form of the `Tokenizer` object.

        DOCS: https://spacy.io/api/tokenizer#to_bytes
        """
        serializers = {
            "vocab": lambda: self.vocab.to_bytes(exclude=exclude),
            "prefix_search": lambda: _get_regex_pattern(self.prefix_search),
            "suffix_search": lambda: _get_regex_pattern(self.suffix_search),
            "infix_finditer": lambda: _get_regex_pattern(self.infix_finditer),
            "token_match": lambda: _get_regex_pattern(self.token_match),
            "url_match": lambda: _get_regex_pattern(self.url_match),
            "exceptions": lambda: dict(sorted(self._rules.items())),
            "faster_heuristics": lambda: self.faster_heuristics,
        }
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, bytes_data, *, exclude=tuple()):
        """Load state from a binary string.

        bytes_data (bytes): The data to load from.
        exclude (list): String names of serialization fields to exclude.
        RETURNS (Tokenizer): The `Tokenizer` object.

        DOCS: https://spacy.io/api/tokenizer#from_bytes
        """
        data = {}
        deserializers = {
            "vocab": lambda b: self.vocab.from_bytes(b, exclude=exclude),
            "prefix_search": lambda b: data.setdefault("prefix_search", b),
            "suffix_search": lambda b: data.setdefault("suffix_search", b),
            "infix_finditer": lambda b: data.setdefault("infix_finditer", b),
            "token_match": lambda b: data.setdefault("token_match", b),
            "url_match": lambda b: data.setdefault("url_match", b),
            "exceptions": lambda b: data.setdefault("rules", b),
            "faster_heuristics": lambda b: data.setdefault("faster_heuristics", b),
        }
        # reset all properties and flush all caches (through rules),
        # reset rules first so that _reload_special_cases is trivial/fast as
        # the other properties are reset
        self.rules = {}
        self.prefix_search = None
        self.suffix_search = None
        self.infix_finditer = None
        self.token_match = None
        self.url_match = None
        msg = util.from_bytes(bytes_data, deserializers, exclude)
        if "prefix_search" in data and isinstance(data["prefix_search"], str):
            self.prefix_search = re.compile(data["prefix_search"]).search
        if "suffix_search" in data and isinstance(data["suffix_search"], str):
            self.suffix_search = re.compile(data["suffix_search"]).search
        if "infix_finditer" in data and isinstance(data["infix_finditer"], str):
            self.infix_finditer = re.compile(data["infix_finditer"]).finditer
        if "token_match" in data and isinstance(data["token_match"], str):
            self.token_match = re.compile(data["token_match"]).match
        if "url_match" in data and isinstance(data["url_match"], str):
            self.url_match = re.compile(data["url_match"]).match
        if "faster_heuristics" in data:
            self.faster_heuristics = data["faster_heuristics"]
        # always load rules last so that all other settings are set before the
        # internal tokenization for the phrase matcher
        if "rules" in data and isinstance(data["rules"], dict):
            self.rules = data["rules"]
        return self


def _get_regex_pattern(regex):
    """Get a pattern string for a regex, or None if the pattern is None."""
    return None if regex is None else regex.__self__.pattern


cdef extern from "<algorithm>" namespace "std" nogil:
    void stdsort "sort"(vector[SpanC].iterator,
                        vector[SpanC].iterator,
                        bint (*)(SpanC, SpanC))


cdef bint len_start_cmp(SpanC a, SpanC b) nogil:
    if a.end - a.start == b.end - b.start:
        return b.start < a.start
    return a.end - a.start < b.end - b.start


cdef bint start_cmp(SpanC a, SpanC b) nogil:
    return a.start < b.start
