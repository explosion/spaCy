import json
from os import path
from collections import defaultdict

from thinc.typedefs cimport atom_t, weight_t

from .typedefs cimport attr_t
from .tokens.doc cimport Doc
from .morphology cimport set_morph_from_dict
from .attrs cimport TAG
from .parts_of_speech cimport NO_TAG, ADJ, ADV, ADP, CONJ, DET, NOUN, NUM, PRON
from .parts_of_speech cimport PRT, VERB, X, PUNCT, EOL, SPACE

 
cdef struct _CachedMorph:
    Morphology morph
    int lemma


cdef class Tagger:
    """A part-of-speech tagger for English"""
    def make_lemmatizer(self):
        return None

    def __init__(self, StringStore strings, data_dir):
        self.mem = Pool()
        model_dir = path.join(data_dir, 'pos')
        self.strings = strings
        cfg = json.load(open(path.join(data_dir, 'pos', 'config.json')))
        self.tag_names = sorted(cfg['tag_names'])
        assert self.tag_names
        self.n_tags = len(self.tag_names)
        self.tag_map = cfg['tag_map']
        cdef int n_tags = len(self.tag_names) + 1

        self.model = Model(n_tags, cfg['templates'], model_dir)
        self._morph_cache = PreshMapArray(n_tags)
        self.tags = <PosTag*>self.mem.alloc(n_tags, sizeof(PosTag))
        for i, tag in enumerate(sorted(self.tag_names)):
            pos, props = self.tag_map[tag]
            self.tags[i].id = i
            self.tags[i].pos = pos
            set_morph_from_dict(&self.tags[i].morph, props)
        if path.exists(path.join(data_dir, 'tokenizer', 'morphs.json')):
            self.load_morph_exceptions(json.load(open(path.join(data_dir, 'tokenizer',
                                                 'morphs.json'))))
        self.lemmatizer = self.make_lemmatizer(data_dir)
        self.freqs = {TAG: defaultdict(int)}
        for tag in self.tag_names:
            self.freqs[TAG][self.strings[tag]] = 1
        self.freqs[TAG][0] = 1

    def __call__(self, Doc tokens):
        """Apply the tagger, setting the POS tags onto the Doc object.

        Args:
            tokens (Doc): The tokens to be tagged.
        """
        if tokens.length == 0:
            return 0
        cdef int i
        cdef const weight_t* scores
        for i in range(tokens.length):
            if tokens.data[i].pos == 0:
                guess = self.predict(i, tokens.data)
                tokens.data[i].tag = self.strings[self.tag_names[guess]]
                self.set_morph(i, &self.tags[guess], tokens.data)

        tokens.is_tagged = True
        tokens._py_tokens = [None] * tokens.length

    def tag_from_strings(self, Doc tokens, object tag_strs):
        cdef int i
        for i in range(tokens.length):
            tokens.data[i].tag = self.strings[tag_strs[i]]
            self.set_morph(i, &self.tags[self.tag_names.index(tag_strs[i])],
                           tokens.data)
        tokens.is_tagged = True
        tokens._py_tokens = [None] * tokens.length

    def train(self, Doc tokens, object gold_tag_strs):
        cdef int i
        cdef int loss
        cdef const weight_t* scores
        golds = [self.tag_names.index(g) if g is not None else -1
                 for g in gold_tag_strs]
        correct = 0
        for i in range(tokens.length):
            guess = self.update(i, tokens.data, golds[i])
            loss = golds[i] != -1 and guess != golds[i]
            tokens.data[i].tag = self.strings[self.tag_names[guess]]
            self.set_morph(i, &self.tags[guess], tokens.data)
            correct += loss == 0
            self.freqs[TAG][tokens.data[i].tag] += 1
        return correct

    cdef int predict(self, int i, const TokenC* tokens) except -1:
        raise NotImplementedError

    cdef int update(self, int i, const TokenC* tokens, int gold) except -1:
        raise NotImplementedError

    cdef int set_morph(self, const int i, const PosTag* tag, TokenC* tokens) except -1:
        tokens[i].pos = tag.pos
        cached = <_CachedMorph*>self._morph_cache.get(tag.id, tokens[i].lex.orth)
        if cached is NULL:
            cached = <_CachedMorph*>self.mem.alloc(1, sizeof(_CachedMorph))
            cached.lemma = self.lemmatize(tag.pos, tokens[i].lex)
            cached.morph = tag.morph
            self._morph_cache.set(tag.id, tokens[i].lex.orth, <void*>cached)
        tokens[i].lemma = cached.lemma
        tokens[i].morph = cached.morph

    cdef int lemmatize(self, const univ_pos_t pos, const LexemeC* lex) except -1:
        if self.lemmatizer is None:
            return lex.orth
        cdef unicode py_string = self.strings[lex.orth]
        if pos != NOUN and pos != VERB and pos != ADJ:
            return lex.orth
        cdef set lemma_strings
        cdef unicode lemma_string
        lemma_strings = self.lemmatizer(py_string, pos)
        lemma_string = sorted(lemma_strings)[0]
        lemma = self.strings[lemma_string]
        return lemma

    def load_morph_exceptions(self, dict exc):
        cdef unicode pos_str
        cdef unicode form_str
        cdef unicode lemma_str
        cdef dict entries
        cdef dict props
        cdef int lemma
        cdef attr_t orth
        cdef int pos
        for pos_str, entries in exc.items():
            pos = self.tag_names.index(pos_str)
            for form_str, props in entries.items():
                lemma_str = props.get('L', form_str)
                orth = self.strings[form_str]
                cached = <_CachedMorph*>self.mem.alloc(1, sizeof(_CachedMorph))
                cached.lemma = self.strings[lemma_str]
                set_morph_from_dict(&cached.morph, props)
                self._morph_cache.set(pos, orth, <void*>cached)
