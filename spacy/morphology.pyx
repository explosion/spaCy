from os import path
import json

from .lemmatizer import Lemmatizer


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


cdef class Morphologizer:
    """Given a POS tag and a Lexeme, find its lemma and morphological analysis.
    """
    def __init__(self, StringStore strings, data_dir):
        self.mem = Pool()
        self.strings = strings
        cfg = json.load(open(path.join(data_dir, 'pos', 'config.json')))
        tag_map = cfg['tag_map']
        tag_names = cfg['tag_names']
        self.lemmatizer = Lemmatizer(path.join(data_dir, '..', 'wordnet'))
        self._lemmas = PreshMapArray(N_UNIV_TAGS)
        self._morph = PreshMapArray(len(tag_names))
        self.tags = <PosTag*>self.mem.alloc(len(tag_names), sizeof(PosTag))
        for i, tag in enumerate(tag_names):
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

    cdef int lemmatize(self, const univ_tag_t pos, const Lexeme* lex) except -1:
        if self.lemmatizer is None:
            return lex.sic
        if pos != NOUN and pos != VERB and pos != ADJ:
            return lex.sic
        cdef int lemma = <int><size_t>self._lemmas.get(pos, lex.sic)
        if lemma != 0:
            return lemma
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
        self._lemmas.set(pos, lex.sic, <void*>lemma)
        return lemma

    cdef int set_morph(self, const int i, TokenC* tokens) except -1:
        cdef const PosTag* tag = &self.tags[tokens[i].pos]
        tokens[i].lemma = self.lemmatize(tag.pos, tokens[i].lex)
        morph = <Morphology*>self._morph.get(tag.id, tokens[i].lemma)
        if morph is NULL:
            self._morph.set(tag.id, tokens[i].lemma, <void*>&tag.morph)
            tokens[i].morph = tag.morph
        else:
            tokens[i].morph = morph[0]
