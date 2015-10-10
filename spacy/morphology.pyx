from os import path
from .lemmatizer import Lemmatizer

try:
    import ujson as json
except ImportError:
    import json

from .parts_of_speech import UNIV_POS_NAMES
from .parts_of_speech cimport ADJ, VERB, NOUN, PUNCT


cdef class Morphology:
    def __init__(self, StringStore string_store, tag_map, lemmatizer):
        self.mem = Pool()
        self.strings = string_store
        self.lemmatizer = lemmatizer
        self.n_tags = len(tag_map) + 1
        self.tag_names = tuple(sorted(tag_map.keys()))
        self.reverse_index = {}
        
        self.rich_tags = <RichTagC*>self.mem.alloc(self.n_tags, sizeof(RichTagC))
        for i, (tag_str, props) in enumerate(sorted(tag_map.items())):
            self.rich_tags[i].id = i
            self.rich_tags[i].name = self.strings[tag_str]
            self.rich_tags[i].morph = 0
            self.rich_tags[i].pos = UNIV_POS_NAMES[props['pos'].upper()]
            self.reverse_index[self.rich_tags[i].name] = i
        self._cache = PreshMapArray(self.n_tags)

    cdef int assign_tag(self, TokenC* token, tag) except -1:
        cdef int tag_id
        if isinstance(tag, basestring):
            tag_id = self.reverse_index[self.strings[tag]]
        else:
            tag_id = tag
        analysis = <MorphAnalysisC*>self._cache.get(tag_id, token.lex.orth)
        if analysis is NULL:
            analysis = <MorphAnalysisC*>self.mem.alloc(1, sizeof(MorphAnalysisC))
            analysis.tag = self.rich_tags[tag_id]
            analysis.lemma = self.lemmatize(analysis.tag.pos, token.lex.orth)
            self._cache.set(tag_id, token.lex.orth, analysis)
        token.lemma = analysis.lemma
        token.pos = analysis.tag.pos
        token.tag = analysis.tag.name
        token.morph = analysis.tag.morph

    cdef int assign_feature(self, uint64_t* morph, feature, value) except -1:
        pass

    def load_morph_exceptions(self, dict exc):
        # Map (form, pos) to (lemma, rich tag)
        cdef unicode pos_str
        cdef unicode form_str
        cdef unicode lemma_str
        cdef dict entries
        cdef dict props
        cdef int lemma
        cdef attr_t orth
        cdef attr_t tag_id
        cdef int pos
        cdef RichTagC rich_tag
        for tag_str, entries in exc.items():
            tag = self.strings[tag_str]
            tag_id = self.reverse_index[tag] 
            rich_tag = self.rich_tags[tag_id]
            for form_str, props in entries.items():
                cached = <MorphAnalysisC*>self.mem.alloc(1, sizeof(MorphAnalysisC))
                cached.tag = rich_tag
                orth = self.strings[form_str]
                for name_str, value_str in props.items():
                    if name_str == 'L':
                        cached.lemma = self.strings[value_str]
                    else:
                        self.assign_feature(&cached.tag.morph, name_str, value_str)
                if cached.lemma == 0:
                    cached.lemma = self.lemmatize(rich_tag.pos, orth)
                self._cache.set(tag_id, orth, <void*>cached)

    def lemmatize(self, const univ_pos_t pos, attr_t orth):
        if self.lemmatizer is None:
            return orth
        cdef unicode py_string = self.strings[orth]
        if pos != NOUN and pos != VERB and pos != ADJ and pos != PUNCT:
            return orth
        cdef set lemma_strings
        cdef unicode lemma_string
        lemma_strings = self.lemmatizer(py_string, pos)
        lemma_string = sorted(lemma_strings)[0]
        lemma = self.strings[lemma_string]
        return lemma
