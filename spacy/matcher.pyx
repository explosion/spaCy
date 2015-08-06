from os import path

from .typedefs cimport attr_t
from .attrs cimport attr_id_t
from .structs cimport TokenC

from cymem.cymem cimport Pool
from libcpp.vector cimport vector

from .attrs cimport LENGTH, ENT_TYPE, ORTH, NORM, LEMMA, LOWER, SHAPE
from .tokens.doc cimport get_token_attr
from .tokens.doc cimport Doc
from .vocab cimport Vocab

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
    pattern[i].spec = <AttrValue*>mem.alloc(1, sizeof(AttrValue))
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
                attr = map_attr_name(attr)
            if isinstance(value, basestring):
                value = string_store[value]
            converted[-1].append((attr, value))
    return converted
    

def map_attr_name(attr):
    attr = attr.upper()
    if attr == 'ORTH':
        return ORTH
    elif attr == 'LEMMA':
        return LEMMA
    elif attr == 'LOWER':
        return LOWER
    elif attr == 'SHAPE':
        return SHAPE
    elif attr == 'NORM':
        return NORM
    else:
        raise Exception("TODO: Finish supporting attr mapping %s" % attr)


cdef class Matcher:
    cdef Pool mem
    cdef Pattern** patterns
    cdef readonly int n_patterns

    def __init__(self, vocab, patterns):
        self.mem = Pool()
        n_patterns = sum([len(specs) for etype, attrs, specs in patterns.values()])
        self.patterns = <Pattern**>self.mem.alloc(n_patterns, sizeof(Pattern*))
        cdef int i = 0
        for entity_key, (etype, attrs, specs) in sorted(patterns.items()):
            if isinstance(entity_key, basestring):
                entity_key = vocab.strings[entity_key]
            if isinstance(etype, basestring):
                etype = vocab.strings[etype]
            elif etype is None:
                etype = -1
            # TODO: Do something more clever about multiple patterns for single
            # entity
            for spec in specs:
                spec = _convert_strings(spec, vocab.strings)
                self.patterns[i] = init_pattern(self.mem, spec, etype)
                i += 1
        self.n_patterns = len(patterns)

    @classmethod
    def from_dir(cls, vocab, data_dir):
        patterns_loc = path.join(data_dir, 'vocab', 'gazetteer.json')
        if path.exists(patterns_loc):
            patterns_data = open(patterns_loc).read()
            patterns = json.loads(patterns_data)
            return cls(vocab, patterns)
        else:
            return cls(vocab, {})

    def __call__(self, Doc doc):
        cdef vector[Pattern*] partials
        cdef int n_partials = 0
        cdef int q = 0
        cdef int i, token_i
        cdef const TokenC* token
        cdef Pattern* state
        matches = []
        for token_i in range(doc.length):
            token = &doc.data[token_i]
            q = 0
            for i in range(partials.size()):
                state = partials.at(i)
                if match(state, token):
                    if is_final(state):
                        matches.append(get_entity(state, token, token_i))
                    else:
                        partials[q] = state + 1
                        q += 1
            partials.resize(q)
            for i in range(self.n_patterns):
                state = self.patterns[i]
                if match(state, token):
                    if is_final(state):
                        matches.append(get_entity(state, token, token_i))
                    else:
                        partials.push_back(state + 1)
        doc.ents = [(e.label, e.start, e.end) for e in doc.ents] + matches
        return matches
