from os import path
import json

from thinc.typedefs cimport atom_t

from ..typedefs cimport univ_tag_t
from ..typedefs cimport NO_TAG, ADJ, ADV, ADP, CONJ, DET, NOUN, NUM, PRON, PRT, VERB
from ..typedefs cimport X, PUNCT, EOL
from ..typedefs cimport id_t
from ..structs cimport TokenC, Morphology, Lexeme
from ..tokens cimport Tokens
from ..morphology cimport set_morph_from_dict
from .lemmatizer import Lemmatizer


cpdef enum en_person_t:
    NO_PERSON
    FIRST
    SECOND
    THIRD
    NON_THIRD


cpdef enum en_number_t:
    NO_NUMBER
    SINGULAR
    PLURAL
    MASS


cpdef enum en_gender_t:
    NO_GENDER
    MASCULINE
    FEMININE
    NEUTER


cpdef enum en_case_t:
    NO_CASE
    NOMINATIVE
    GENITIVE
    ACCUSATIVE
    REFLEXIVE
    DEMONYM


cpdef enum en_tenspect_t:
    NO_TENSE
    BASE_VERB
    PRESENT
    PAST
    PASSIVE
    ING
    MODAL


cpdef enum misc_t:
    NO_MISC
    COMPARATIVE
    SUPERLATIVE
    RELATIVE
    NAME


cpdef enum:
    P2_sic
    P2_cluster
    P2_shape
    P2_prefix
    P2_suffix
    P2_pos
    P2_lemma
    P2_pos_type

    P1_sic
    P1_cluster
    P1_shape
    P1_prefix
    P1_suffix
    P1_pos
    P1_lemma
    P1_pos_type

    W_sic
    W_cluster
    W_shape
    W_prefix
    W_suffix
    W_pos
    W_lemma
    W_pos_type

    N1_sic
    N1_cluster
    N1_shape
    N1_prefix
    N1_suffix
    N1_pos
    N1_lemma
    N1_pos_type

    N2_sic
    N2_cluster
    N2_shape
    N2_prefix
    N2_suffix
    N2_pos
    N2_lemma
    N2_pos_type

    N_CONTEXT_FIELDS


POS_TAGS = {
    'NULL': (NO_TAG, {}),
    'EOL': (EOL, {}),
    'CC': (CONJ, {}),
    'CD': (NUM, {}),
    'DT': (DET, {}),
    'EX': (DET, {}),
    'FW': (X, {}),
    'IN': (ADP, {}),
    'JJ': (ADJ, {}),
    'JJR': (ADJ, {'misc': COMPARATIVE}),
    'JJS': (ADJ, {'misc': SUPERLATIVE}),
    'LS': (X, {}),
    'MD': (VERB, {'tenspect': MODAL}),
    'NN': (NOUN, {}),
    'NNS': (NOUN, {'number': PLURAL}),
    'NNP': (NOUN, {'misc': NAME}),
    'NNPS': (NOUN, {'misc': NAME, 'number': PLURAL}),
    'PDT': (DET, {}),
    'POS': (PRT, {'case': GENITIVE}),
    'PRP': (NOUN, {}),
    'PRP$': (NOUN, {'case': GENITIVE}),
    'RB': (ADV, {}),
    'RBR': (ADV, {'misc': COMPARATIVE}),
    'RBS': (ADV, {'misc': SUPERLATIVE}),
    'RP': (PRT, {}),
    'SYM': (X, {}),
    'TO': (PRT, {}),
    'UH': (X, {}),
    'VB': (VERB, {}),
    'VBD': (VERB, {'tenspect': PAST}),
    'VBG': (VERB, {'tenspect': ING}),
    'VBN': (VERB, {'tenspect': PASSIVE}),
    'VBP': (VERB, {'tenspect': PRESENT}),
    'VBZ': (VERB, {'tenspect': PRESENT, 'person': THIRD}),
    'WDT': (DET, {'misc': RELATIVE}),
    'WP': (PRON, {'misc': RELATIVE}),
    'WP$': (PRON, {'misc': RELATIVE, 'case': GENITIVE}),
    'WRB': (ADV, {'misc': RELATIVE}),
    '!': (PUNCT, {}),
    '#': (PUNCT, {}),
    '$': (PUNCT, {}),
    "''": (PUNCT, {}),
    "(": (PUNCT, {}),
    ")": (PUNCT, {}),
    "-LRB-": (PUNCT, {}),
    "-RRB-": (PUNCT, {}),
    ".": (PUNCT, {}),
    ",": (PUNCT, {}),
    "``": (PUNCT, {}),
    ":": (PUNCT, {}),
    "?": (PUNCT, {}),
}


POS_TEMPLATES = (
    (W_sic,),
    (P1_lemma, P1_pos),
    (P2_lemma, P2_pos),
    (N1_sic,),
    (N2_sic,),

    (W_suffix,),
    (W_prefix,),

    (P1_pos,),
    (P2_pos,),
    (P1_pos, P2_pos),
    (P1_pos, W_sic),
    (P1_suffix,),
    (N1_suffix,),

    (W_shape,),
    (W_cluster,),
    (N1_cluster,),
    (N2_cluster,),
    (P1_cluster,),
    (P2_cluster,),

    (W_pos_type,),
    (N1_pos_type,),
    (N1_pos_type,),
    (P1_pos, W_pos_type, N1_pos_type),
)


cdef struct _CachedMorph:
    Morphology morph
    int lemma


cdef class EnPosTagger(Tagger):
    def __init__(self, StringStore strings, data_dir):
        model_dir = path.join(data_dir, 'pos')
        Tagger.__init__(self, path.join(model_dir))
        self.strings = strings
        cfg = json.load(open(path.join(data_dir, 'pos', 'config.json')))
        self.tag_names = sorted(cfg['tag_names'])
        self.tag_map = cfg['tag_map']
        cdef int n_tags = len(self.tag_names) + 1
        self._morph_cache = PreshMapArray(n_tags)
        self.tags = <PosTag*>self.mem.alloc(n_tags, sizeof(PosTag))
        for i, tag in enumerate(sorted(self.tag_names)):
            pos, props = self.tag_map[tag]
            self.tags[i].id = i
            self.tags[i].pos = pos
            set_morph_from_dict(&self.tags[i].morph, props)
        if path.exists(path.join(data_dir, 'morphs.json')):
            self.load_morph_exceptions(json.load(open(path.join(data_dir, 'morphs.json'))))
        self.lemmatizer = Lemmatizer(path.join(data_dir, 'wordnet'), NOUN, VERB, ADJ)

    def __call__(self, Tokens tokens):
        cdef int i
        cdef atom_t[N_CONTEXT_FIELDS] context
        cdef TokenC* t = tokens.data
        for i in range(tokens.length):
            fill_context(context, i, t)
            t[i].pos = self.predict(context)
            self.set_morph(i, t)

    def train(self, Tokens tokens, golds):
        cdef int i
        cdef atom_t[N_CONTEXT_FIELDS] context
        c = 0
        cdef TokenC* t = tokens.data
        for i in range(tokens.length):
            fill_context(context, i, t)
            t[i].pos = self.predict(context, [golds[i]])
            self.set_morph(i, t)
            c += t[i].pos == golds[i]
        return c

    cdef int set_morph(self, const int i, TokenC* tokens) except -1:
        cdef const PosTag* tag = &self.tags[tokens[i].pos]
        cached = <_CachedMorph*>self._morph_cache.get(tag.id, tokens[i].lex.sic)
        if cached is NULL:
            cached = <_CachedMorph*>self.mem.alloc(1, sizeof(_CachedMorph))
            cached.lemma = self.lemmatize(tag.pos, tokens[i].lex)
            cached.morph = tag.morph
            self._morph_cache.set(tag.id, tokens[i].lex.sic, <void*>cached)
        tokens[i].lemma = cached.lemma
        tokens[i].morph = cached.morph

    cdef int lemmatize(self, const univ_tag_t pos, const Lexeme* lex) except -1:
        if self.lemmatizer is None:
            return lex.sic
        cdef bytes py_string = self.strings[lex.sic]
        if pos != NOUN and pos != VERB and pos != ADJ:
            return lex.sic
        cdef set lemma_strings
        cdef bytes lemma_string
        lemma_strings = self.lemmatizer(py_string, pos)
        lemma_string = sorted(lemma_strings)[0]
        lemma = self.strings.intern(lemma_string, len(lemma_string)).i
        return lemma

    def load_morph_exceptions(self, dict exc):
        cdef unicode pos_str
        cdef unicode form_str
        cdef unicode lemma_str
        cdef dict entries
        cdef dict props
        cdef int lemma
        cdef id_t sic
        cdef int pos
        for pos_str, entries in exc.items():
            pos = self.tag_names.index(pos_str)
            for form_str, props in entries.items():
                lemma_str = props.get('L', form_str)
                sic = self.strings[form_str]
                cached = <_CachedMorph*>self.mem.alloc(1, sizeof(_CachedMorph))
                cached.lemma = self.strings[lemma_str]
                set_morph_from_dict(&cached.morph, props)
                self._morph_cache.set(pos, sic, <void*>cached)
 

cdef int fill_context(atom_t* context, const int i, const TokenC* tokens) except -1:
    _fill_from_token(&context[P2_sic], &tokens[i-2])
    _fill_from_token(&context[P1_sic], &tokens[i-1])
    _fill_from_token(&context[W_sic], &tokens[i])
    _fill_from_token(&context[N1_sic], &tokens[i+1])
    _fill_from_token(&context[N2_sic], &tokens[i+2])


cdef inline void _fill_from_token(atom_t* context, const TokenC* t) nogil:
    context[0] = t.lex.sic
    context[1] = t.lex.cluster
    context[2] = t.lex.shape
    context[3] = t.lex.prefix
    context[4] = t.lex.suffix
    context[5] = t.pos
    context[6] = t.lemma
    context[7] = t.lex.pos_type
