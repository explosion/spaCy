from os import path
from .lemmatizer import Lemmatizer

try:
    import ujson as json
except ImportError:
    import json

from .parts_of_speech import UNIV_POS_NAMES
from .parts_of_speech cimport ADJ, VERB, NOUN


cdef class Morphology:
    @classmethod
    def from_dir(cls, data_dir, lemmatizer=None):
        tag_map = json.load(open(path.join(data_dir, 'tag_map.json')))
        if lemmatizer is None:
            lemmatizer = Lemmatizer.from_dir(data_dir)
        return cls(tag_map, {}, lemmatizer)

    def __init__(self, string_store, tag_map, lemmatizer):
        self.mem = Pool()
        self.strings = string_store
        self.lemmatizer = lemmatizer
        self.n_tags = len(tag_map)
        self.tag_names = tuple(sorted(tag_map.keys()))
        self.reverse_index = {}
        for i, (tag_str, props) in enumerate(sorted(tag_map.items())):
            self.rich_tags[i].id = i
            self.rich_tags[i].name = self.strings[tag_str]
            self.rich_tags[i].morph = 0
            self.reverse_index[self.rich_tags[i].name] = i
        self._cache = PreshMapArray(self.n_tags)

    cdef int assign_tag(self, TokenC* token, tag) except -1:
        cdef int tag_id = self.strings[tag] if isinstance(tag, basestring) else tag
        analysis = <MorphAnalysisC*>self._cache.get(tag_id, token.lex.orth)
        if analysis is NULL:
            analysis = <MorphAnalysisC*>self.mem.alloc(1, sizeof(MorphAnalysisC))
            analysis.tag = self.rich_tags[tag_id]
            analysis.lemma = self.lemmatize(tag, token.lex.orth)
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
        cdef int pos
        for tag_str, entries in exc.items():
            tag = self.strings[tag_str]
            rich_tag = self.rich_tags[self.reverse_index[tag]]
            for form_str, props in entries.items():
                cached = <MorphAnalysisC*>self.mem.alloc(1, sizeof(MorphAnalysisC))
                orth = self.strings[form_str]
                for name_str, value_str in props.items():
                    if name_str == 'L':
                        cached.lemma = self.strings[value_str]
                    else:
                        self.assign_feature(&cached.tag.morph, name_str, value_str)
                if cached.lemma == 0:
                    cached.lemma = self.lemmatize(rich_tag.pos, orth)
                self._cache.set(rich_tag.pos, orth, <void*>cached)

    def lemmatize(self, const univ_pos_t pos, attr_t orth):
        if self.lemmatizer is None:
            return orth
        cdef unicode py_string = self.strings[orth]
        if pos != NOUN and pos != VERB and pos != ADJ:
            return orth
        cdef set lemma_strings
        cdef unicode lemma_string
        lemma_strings = self.lemmatizer(py_string, pos)
        lemma_string = sorted(lemma_strings)[0]
        lemma = self.strings[lemma_string]
        return lemma
