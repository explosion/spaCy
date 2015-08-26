from os import path

try:
    import ujson as json
except ImportError:
    import json

from spacy.parts_of_speech import UNIV_POS_NAMES
    

cdef class Morphology:
    def __init__(self, tag_map, fused_tokens, lemmatizer):
        self.tag_map = tag_map
        self.n_tags = len(tag_map)
        self.tag_names = tuple(sorted(tag_map.keys()))
        self.tag_ids = {}
        for i, tag_str in enumerate(self.tag_names):
            self.tag_ids[tag_str] = i

    @classmethod
    def from_dir(cls, data_dir):
        tag_map = json.load(open(path.join(data_dir, 'tag_map.json')))
        return cls(tag_map, {}, None)

    cdef int assign_tag(self, TokenC* token, int tag) except -1:
        props = self.tag_map[self.tag_names[tag]]
        token.pos = UNIV_POS_NAMES[props['pos'].upper()]
        token.tag = tag
        #token.inflection = # TODO

    cdef int assign_from_dict(self, TokenC* token, props) except -1:
        pass

    def load_morph_exceptions(self, dict exc):
        pass
        # Map (form, pos) to (lemma, inflection)
        #cdef unicode pos_str
        #cdef unicode form_str
        #cdef unicode lemma_str
        #cdef dict entries
        #cdef dict props
        #cdef int lemma
        #cdef attr_t orth
        #cdef int pos
        #for pos_str, entries in exc.items():
        #    pos = self.tag_names.index(pos_str)
        #    for form_str, props in entries.items():
        #        lemma_str = props.get('L', form_str)
        #        orth = self.strings[form_str]
        #        cached = <InflectedLemma*>self.mem.alloc(1, sizeof(InflectedLemma))
        #        cached.lemma = self.strings[lemma_str]
        #        set_morph_from_dict(&cached.morph, props)
        #        self._morph_cache.set(pos, orth, <void*>cached)


#cdef int set_morph_from_dict(Morphology* morph, dict props) except -1:
#    morph.number = props.get('number', 0)
#    morph.tenspect = props.get('tenspect', 0)
#    morph.mood = props.get('mood', 0)
#    morph.gender = props.get('gender', 0)
#    morph.person = props.get('person', 0)
#    morph.case = props.get('case', 0)
#    morph.misc = props.get('misc', 0)
#
#
#cdef class Morphology:
#    cdef Pool mem
#    cdef PreshMap table
#
#    def __init__(self, tags, exceptions):
#        pass
#
#    def __getitem__(self, hash_t id_):
#        pass
#
#    cdef const InflectionC* get(self, hash_t key) except NULL:
#        pass
#
#    cdef MorphAnalysis analyse(const TokenC* token) except -1:
#        cdef struct MorphAnalysis morphology
#        tokens[i].pos = tag.pos
#        cached = <_CachedMorph*>self._morph_cache.get(tag.id, tokens[i].lex.orth)
#        if cached is NULL:
#            cached = <_CachedMorph*>self.mem.alloc(1, sizeof(_CachedMorph))
#            cached.lemma = self.lemmatize(tag.pos, tokens[i].lex)
#            cached.morph = tag.morph
#            self._morph_cache.set(tag.id, tokens[i].lex.orth, <void*>cached)
#        tokens[i].lemma = cached.lemma
#        tokens[i].morph = cached.morph
#        
#    cdef int lemmatize(self, const univ_pos_t pos, const LexemeC* lex) except -1:
#        if self.lemmatizer is None:
#            return lex.orth
#        cdef unicode py_string = self.strings[lex.orth]
#        if pos != NOUN and pos != VERB and pos != ADJ:
#            return lex.orth
#        cdef set lemma_strings
#        cdef unicode lemma_string
#        lemma_strings = self.lemmatizer(py_string, pos)
#        lemma_string = sorted(lemma_strings)[0]
#        lemma = self.strings[lemma_string]
#        return lemma
#        
#
#cdef class Inflection:
#    cdef InflectionC* c
#
#    def __init__(self, container, id_):
#        self.c = container[id_]
#        self.container = container
#        
#        for i, feat_id in enumerate(feat_ids):
#            feature, value = parse_id(feat_id)
#            self.add_value(feature, value, True)
#
#    def has(self, Value_t feat_value_id):
#        part = feat_value_id % 64
#        bit = feat_value_id / 64
#        if self.value_set[part] & bit:
#            return True
#        else:
#            return False
#
#    property pos: def __get__(self): return self.c.pos
#
#    property id: def __get__(self): return self.c.id
#
#    property features:
#        pass
