# cython: profile=True
# cython: embedsignature=True
from os import path
import json

from .typedefs cimport id_t, univ_tag_t
from .typedefs cimport NO_TAG, ADJ, ADV, ADP, CONJ, DET, NOUN, NUM, PRON, PRT
from .typedefs cimport VERB, X, PUNCT, EOL
from . import util


UNIV_TAGS = {
    'NULL': NO_TAG,
    'ADJ': ADJ,
    'ADV': ADV,
    'ADP': ADP,
    'CONJ': CONJ,
    'DET': DET,
    'NOUN': NOUN,
    'NUM': NUM,
    'PRON': PRON,
    'PRT': PRT,
    'VERB': VERB,
    'X': X,
    '.': PUNCT,
    'EOL': EOL
}


cdef struct _Cached:
    Morphology morph
    int lemma


cdef class Morphologizer:
    """Given a POS tag and a Lexeme, find its lemma and morphological analysis.
    """
    def __init__(self, StringStore strings, object lemmatizer,
                 irregulars=None, tag_map=None, tag_names=None):
        self.mem = Pool()
        self.strings = strings
        self.tag_names = tag_names
        self.lemmatizer = lemmatizer
        self._cache = PreshMapArray(len(self.tag_names))
        self.tags = <PosTag*>self.mem.alloc(len(self.tag_names), sizeof(PosTag))
        for i, tag in enumerate(self.tag_names):
            pos, props = tag_map[tag]
            self.tags[i].id = i
            self.tags[i].pos = pos
            self.tags[i].morph.number = props.get('number', 0)
            self.tags[i].morph.tenspect = props.get('tenspect', 0)
            self.tags[i].morph.mood = props.get('mood', 0)
            self.tags[i].morph.gender = props.get('gender', 0)
            self.tags[i].morph.person = props.get('person', 0)
            self.tags[i].morph.case = props.get('case', 0)
            self.tags[i].morph.misc = props.get('misc', 0)
        if irregulars is not None:
            self.load_exceptions(irregulars)

    @classmethod
    def from_dir(cls, StringStore strings, object lemmatizer, data_dir):
        tagger_cfg = json.loads(open(path.join(data_dir, 'pos', 'config.json')).read())
        tag_map = tagger_cfg['tag_map']
        tag_names = tagger_cfg['tag_names']
        irregulars = json.loads(open(path.join(data_dir, 'morphs.json')).read())
        return cls(strings, lemmatizer, tag_map=tag_map, irregulars=irregulars,
                   tag_names=tag_names)

    cdef int lemmatize(self, const univ_tag_t pos, const Lexeme* lex) except -1:
        if self.lemmatizer is None:
            return lex.sic
        if pos != NOUN and pos != VERB and pos != ADJ:
            return lex.sic
        cdef bytes py_string = self.strings[lex.sic]
        cdef set lemma_strings
        cdef bytes lemma_string
        if pos == NOUN:
            lemma_strings = self.lemmatizer.noun(py_string)
        elif pos == VERB:
            lemma_strings = self.lemmatizer.verb(py_string)
        else:
            assert pos == ADJ
            lemma_strings = self.lemmatizer.adj(py_string)
        lemma_string = sorted(lemma_strings)[0]
        lemma = self.strings.intern(lemma_string, len(lemma_string)).i
        return lemma

    cdef int set_morph(self, const int i, TokenC* tokens) except -1:
        cdef const PosTag* tag = &self.tags[tokens[i].pos]
        cached = <_Cached*>self._cache.get(tag.id, tokens[i].lex.sic)
        if cached is NULL:
            cached = <_Cached*>self.mem.alloc(1, sizeof(_Cached))
            cached.lemma = self.lemmatize(tag.pos, tokens[i].lex)
            cached.morph = tag.morph
            self._cache.set(tag.id, tokens[i].lex.sic, <void*>cached)
        tokens[i].lemma = cached.lemma
        tokens[i].morph = cached.morph

    def load_exceptions(self, dict exc):
        cdef unicode pos_str
        cdef unicode form_str
        cdef unicode lemma_str
        cdef dict entries
        cdef dict props
        cdef int lemma
        cdef id_t sic
        cdef univ_tag_t pos
        for pos_str, entries in exc.items():
            pos = self.tag_names.index(pos_str)
            for form_str, props in entries.items():
                lemma_str = props.get('L', form_str)
                sic = self.strings[form_str]
                cached = <_Cached*>self.mem.alloc(1, sizeof(_Cached))
                cached.lemma = self.strings[lemma_str]
                set_morph_from_dict(&cached.morph, props)
                self._cache.set(pos, sic, <void*>cached)
                

cdef int set_morph_from_dict(Morphology* morph, dict props) except -1:
    morph.number = props.get('number', 0)
    morph.tenspect = props.get('tenspect', 0)
    morph.mood = props.get('mood', 0)
    morph.gender = props.get('gender', 0)
    morph.person = props.get('person', 0)
    morph.case = props.get('case', 0)
    morph.misc = props.get('misc', 0)
