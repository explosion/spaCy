# cython: profile=True
from __future__ import unicode_literals

from os import path

from .typedefs cimport attr_t
from .typedefs cimport hash_t
from .attrs cimport attr_id_t
from .structs cimport TokenC, LexemeC
from .lexeme cimport Lexeme

from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap
from libcpp.vector cimport vector
from murmurhash.mrmr cimport hash64

from .attrs cimport LENGTH, ENT_TYPE, ORTH, NORM, LEMMA, LOWER, SHAPE
from . import attrs
from .tokens.doc cimport get_token_attr
from .tokens.doc cimport Doc
from .vocab cimport Vocab

from .attrs import FLAG61 as U_ENT
from .util import get_package

from .attrs import FLAG60 as B2_ENT
from .attrs import FLAG59 as B3_ENT
from .attrs import FLAG58 as B4_ENT
from .attrs import FLAG57 as B5_ENT
from .attrs import FLAG56 as B6_ENT
from .attrs import FLAG55 as B7_ENT
from .attrs import FLAG54 as B8_ENT
from .attrs import FLAG53 as B9_ENT
from .attrs import FLAG52 as B10_ENT

from .attrs import FLAG51 as I3_ENT
from .attrs import FLAG50 as I4_ENT
from .attrs import FLAG49 as I5_ENT
from .attrs import FLAG48 as I6_ENT
from .attrs import FLAG47 as I7_ENT
from .attrs import FLAG46 as I8_ENT
from .attrs import FLAG45 as I9_ENT
from .attrs import FLAG44 as I10_ENT

from .attrs import FLAG43 as L2_ENT
from .attrs import FLAG42 as L3_ENT
from .attrs import FLAG41 as L4_ENT
from .attrs import FLAG40 as L5_ENT
from .attrs import FLAG39 as L6_ENT
from .attrs import FLAG38 as L7_ENT
from .attrs import FLAG37 as L8_ENT
from .attrs import FLAG36 as L9_ENT
from .attrs import FLAG35 as L10_ENT


try:
    import ujson as json
except ImportError:
    import json


cdef struct AttrValue:
    attr_id_t attr
    attr_t value


cdef struct Pattern:
    AttrValue* spec
    int length


cdef Pattern* init_pattern(Pool mem, object token_specs, attr_t entity_type) except NULL:
    pattern = <Pattern*>mem.alloc(len(token_specs) + 1, sizeof(Pattern))
    cdef int i
    for i, spec in enumerate(token_specs):
        pattern[i].spec = <AttrValue*>mem.alloc(len(spec), sizeof(AttrValue))
        pattern[i].length = len(spec)
        for j, (attr, value) in enumerate(spec):
            pattern[i].spec[j].attr = attr
            pattern[i].spec[j].value = value
    i = len(token_specs)
    pattern[i].spec = <AttrValue*>mem.alloc(2, sizeof(AttrValue))
    pattern[i].spec[0].attr = ENT_TYPE
    pattern[i].spec[0].value = entity_type
    pattern[i].spec[1].attr = LENGTH
    pattern[i].spec[1].value = len(token_specs)
    pattern[i].length = 0
    return pattern


cdef int match(const Pattern* pattern, const TokenC* token) except -1:
    cdef int i
    for i in range(pattern.length):
        if get_token_attr(token, pattern.spec[i].attr) != pattern.spec[i].value:
            return False
    return True


cdef int is_final(const Pattern* pattern) except -1:
    return (pattern + 1).length == 0


cdef object get_entity(const Pattern* pattern, const TokenC* tokens, int i):
    pattern += 1
    i += 1
    return (pattern.spec[0].value, i - pattern.spec[1].value, i)


def _convert_strings(token_specs, string_store):
    converted = []
    for spec in token_specs:
        converted.append([])
        for attr, value in spec.items():
            if isinstance(attr, basestring):
                attr = attrs.IDS.get(attr.upper())
            if isinstance(value, basestring):
                value = string_store[value]
            if isinstance(value, bool):
                value = int(value)
            if attr is not None:
                converted[-1].append((attr, value))
    return converted


def get_bilou(length):
    if length == 1:
        return [U_ENT]
    elif length == 2:
        return [B2_ENT, L2_ENT]
    elif length == 3:
        return [B3_ENT, I3_ENT, L3_ENT]
    elif length == 4:
        return [B4_ENT, I4_ENT, I4_ENT, L4_ENT]
    elif length == 5:
        return [B5_ENT, I5_ENT, I5_ENT, I5_ENT, L5_ENT]
    elif length == 6:
        return [B6_ENT, I6_ENT, I6_ENT, I6_ENT, I6_ENT, L6_ENT]
    elif length == 7:
        return [B7_ENT, I7_ENT, I7_ENT, I7_ENT, I7_ENT, I7_ENT, L7_ENT]
    elif length == 8:
        return [B8_ENT, I8_ENT, I8_ENT, I8_ENT, I8_ENT, I8_ENT, I8_ENT, L8_ENT]
    elif length == 9:
        return [B9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, L9_ENT]
    elif length == 10:
        return [B10_ENT, I10_ENT, I10_ENT, I10_ENT, I10_ENT, I10_ENT, I10_ENT,
                I10_ENT, I10_ENT, L10_ENT]
    else:
        raise ValueError("Max length currently 10 for phrase matching")


cdef class Matcher:
    cdef Pool mem
    cdef vector[Pattern*] patterns
    cdef readonly Vocab vocab
    cdef object _patterns

    @classmethod
    def load(cls, data_dir, Vocab vocab):
        return cls.from_package(get_package(data_dir), vocab=vocab)

    @classmethod
    def from_package(cls, package, Vocab vocab):
        patterns = package.load_json(('vocab', 'gazetteer.json'))
        return cls(vocab, patterns)

    def __init__(self, vocab, patterns={}):
        self._patterns = dict(patterns) # Make sure we own the object
        self.vocab = vocab
        self.mem = Pool()
        self.vocab = vocab
        for entity_key, (etype, attrs, specs) in sorted(self._patterns.items()):
            self.add(entity_key, etype, attrs, specs)

    def __reduce__(self):
        return (self.__class__, (self.vocab, self._patterns), None, None)
    
    property n_patterns:
        def __get__(self): return self.patterns.size()

    def add(self, entity_key, etype, attrs, specs):
        self._patterns[entity_key] = (etype, dict(attrs), list(specs))
        if isinstance(entity_key, basestring):
            entity_key = self.vocab.strings[entity_key]
        if isinstance(etype, basestring):
            etype = self.vocab.strings[etype]
        elif etype is None:
            etype = -1
        # TODO: Do something more clever about multiple patterns for single
        # entity
        for spec in specs:
            spec = _convert_strings(spec, self.vocab.strings)
            self.patterns.push_back(init_pattern(self.mem, spec, etype))

    def __call__(self, Doc doc, acceptor=None):
        cdef vector[Pattern*] partials
        cdef int n_partials = 0
        cdef int q = 0
        cdef int i, token_i
        cdef const TokenC* token
        cdef Pattern* state
        matches = []
        for token_i in range(doc.length):
            token = &doc.c[token_i]
            q = 0
            # Go over the open matches, extending or finalizing if able. Otherwise,
            # we over-write them (q doesn't advance)
            for state in partials:
                if match(state, token):
                    if is_final(state):
                        label, start, end = get_entity(state, token, token_i)
                        if acceptor is None or acceptor(doc, label, start, end):
                            matches.append((label, start, end))
                    else:
                        partials[q] = state + 1
                        q += 1
            partials.resize(q)
            # Check whether we open any new patterns on this token
            for state in self.patterns:
                if match(state, token):
                    if is_final(state):
                        label, start, end = get_entity(state, token, token_i)
                        if acceptor is None or acceptor(doc, label, start, end):
                            matches.append((label, start, end))
                    else:
                        partials.push_back(state + 1)
        seen = set()
        filtered = []
        for label, start, end in sorted(matches, key=lambda m: (m[1], -(m[1] - m[2]))):
            if all(i in seen for i in range(start, end)):
                continue
            else:
                for i in range(start, end):
                    seen.add(i)
                filtered.append((label, start, end))
        doc.ents = [(e.label, e.start, e.end) for e in doc.ents] + filtered
        return matches

    def pipe(self, docs, batch_size=1000, n_threads=2):
        for doc in docs:
            self(doc)
            yield doc


cdef class PhraseMatcher:
    cdef Pool mem
    cdef Vocab vocab
    cdef Matcher matcher
    cdef PreshMap phrase_ids

    cdef int max_length
    cdef attr_t* _phrase_key

    def __init__(self, Vocab vocab, phrases, max_length=10):
        self.mem = Pool()
        self._phrase_key = <attr_t*>self.mem.alloc(max_length, sizeof(attr_t))
        self.max_length = max_length
        self.vocab = vocab
        self.matcher = Matcher(self.vocab, {})
        self.phrase_ids = PreshMap()
        for phrase in phrases:
            if len(phrase) < max_length:
                self.add(phrase)

        abstract_patterns = []
        for length in range(1, max_length):
            abstract_patterns.append([{tag: True} for tag in get_bilou(length)])
        self.matcher.add('Candidate', 'MWE', {}, abstract_patterns)

    def add(self, Doc tokens):
        cdef int length = tokens.length
        assert length < self.max_length
        tags = get_bilou(length)
        assert len(tags) == length, length
        
        cdef int i
        for i in range(self.max_length):
            self._phrase_key[i] = 0
        for i, tag in enumerate(tags):
            lexeme = self.vocab[tokens.c[i].lex.orth]
            lexeme.set_flag(tag, True)
            self._phrase_key[i] = lexeme.orth
        cdef hash_t key = hash64(self._phrase_key, self.max_length * sizeof(attr_t), 0)
        self.phrase_ids[key] = True

    def __call__(self, Doc doc):
        matches = []
        for label, start, end in self.matcher(doc, acceptor=self.accept_match):
            cand = doc[start : end]
            start = cand[0].idx
            end = cand[-1].idx + len(cand[-1])
            matches.append((start, end, cand.root.tag_, cand.text, 'MWE'))
        for match in matches:
            doc.merge(*match)
        return matches

    def pipe(self, stream, batch_size=1000, n_threads=2):
        for doc in stream:
            self(doc)
            yield doc

    def accept_match(self, Doc doc, int label, int start, int end):
        assert (end - start) < self.max_length
        cdef int i, j
        for i in range(self.max_length):
            self._phrase_key[i] = 0
        for i, j in enumerate(range(start, end)):
            self._phrase_key[i] = doc.c[j].lex.orth
        cdef hash_t key = hash64(self._phrase_key, self.max_length * sizeof(attr_t), 0)
        if self.phrase_ids.get(key):
            return True
        else:
            return False
