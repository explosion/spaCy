from os import path
import json
import os
import shutil

from libc.string cimport memset

from cymem.cymem cimport Address
from thinc.typedefs cimport atom_t, weight_t

from ..parts_of_speech cimport univ_pos_t
from ..parts_of_speech cimport NO_TAG, ADJ, ADV, ADP, CONJ, DET, NOUN, NUM, PRON

from ..parts_of_speech cimport PRT, VERB, X, PUNCT, EOL
from ..typedefs cimport id_t
from ..structs cimport TokenC, Morphology, LexemeC
from ..tokens cimport Tokens
from ..morphology cimport set_morph_from_dict
from .._ml cimport arg_max

from .attrs cimport IS_ALPHA, IS_PUNCT, LIKE_NUM, LIKE_URL

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
    P2_orth
    P2_cluster
    P2_shape
    P2_prefix
    P2_suffix
    P2_pos
    P2_lemma
    P2_flags

    P1_orth
    P1_cluster
    P1_shape
    P1_prefix
    P1_suffix
    P1_pos
    P1_lemma
    P1_flags

    W_orth
    W_cluster
    W_shape
    W_prefix
    W_suffix
    W_pos
    W_lemma
    W_flags

    N1_orth
    N1_cluster
    N1_shape
    N1_prefix
    N1_suffix
    N1_pos
    N1_lemma
    N1_flags

    N2_orth
    N2_cluster
    N2_shape
    N2_prefix
    N2_suffix
    N2_pos
    N2_lemma
    N2_flags

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
    'PRP': (PRON, {}),
    'PRP$': (PRON, {'case': GENITIVE}),
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
    "ADD": (X, {}),
    "NFP": (PUNCT, {}),
    "GW": (X, {}),
    "AFX": (X, {}),
    "HYPH": (PUNCT, {}),
    "XX": (X, {}),
    "BES": (VERB, {'tenspect': PRESENT, 'person': THIRD}),
    "HVS": (VERB, {'tenspect': PRESENT, 'person': THIRD})
}


POS_TEMPLATES = (
    (W_orth,),
    (P1_lemma, P1_pos),
    (P2_lemma, P2_pos),
    (N1_orth,),
    (N2_orth,),

    (W_suffix,),
    (W_prefix,),

    (P1_pos,),
    (P2_pos,),
    (P1_pos, P2_pos),
    (P1_pos, W_orth),
    (P1_suffix,),
    (N1_suffix,),

    (W_shape,),
    (W_cluster,),
    (N1_cluster,),
    (N2_cluster,),
    (P1_cluster,),
    (P2_cluster,),

    (W_flags,),
    (N1_flags,),
    (N2_flags,),
    (P1_flags,),
    (P2_flags,),
)


cdef struct _CachedMorph:
    Morphology morph
    int lemma


def setup_model_dir(tag_names, tag_map, templates, model_dir):
    if path.exists(model_dir):
        shutil.rmtree(model_dir)
    os.mkdir(model_dir)
    config = {
        'templates': templates,
        'tag_names': tag_names,
        'tag_map': tag_map
    }
    with open(path.join(model_dir, 'config.json'), 'w') as file_:
        json.dump(config, file_)


cdef class EnPosTagger:
    """A part-of-speech tagger for English"""
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
        self.lemmatizer = Lemmatizer(path.join(data_dir, 'wordnet'), NOUN, VERB, ADJ)

    def __call__(self, Tokens tokens):
        """Apply the tagger, setting the POS tags onto the Tokens object.

        Args:
            tokens (Tokens): The tokens to be tagged.
        """
        if tokens.length == 0:
            return 0
        cdef int i
        cdef atom_t[N_CONTEXT_FIELDS] context
        cdef const weight_t* scores
        for i in range(tokens.length):
            if tokens.data[i].pos == 0:
                fill_context(context, i, tokens.data)
                scores = self.model.score(context)
                guess = arg_max(scores, self.model.n_classes)
                tokens.data[i].tag = self.strings[self.tag_names[guess]]
                self.set_morph(i, &self.tags[guess], tokens.data)

        tokens.is_tagged = True
        tokens._py_tokens = [None] * tokens.length

    def tag_from_strings(self, Tokens tokens, object tag_strs):
        cdef int i
        for i in range(tokens.length):
            tokens.data[i].tag = self.strings[tag_strs[i]]
            self.set_morph(i, &self.tags[self.tag_names.index(tag_strs[i])],
                           tokens.data)
        tokens.is_tagged = True
        tokens._py_tokens = [None] * tokens.length

    def train(self, Tokens tokens, object gold_tag_strs):
        cdef int i
        cdef int loss
        cdef atom_t[N_CONTEXT_FIELDS] context
        cdef const weight_t* scores
        golds = [self.tag_names.index(g) if g is not None else -1
                 for g in gold_tag_strs]
        correct = 0
        for i in range(tokens.length):
            fill_context(context, i, tokens.data)
            scores = self.model.score(context)
            guess = arg_max(scores, self.model.n_classes)
            loss = guess != golds[i] if golds[i] != -1 else 0
            self.model.update(context, guess, golds[i], loss)
            tokens.data[i].tag = self.strings[self.tag_names[guess]]
            self.set_morph(i, &self.tags[guess], tokens.data)
            correct += loss == 0
        return correct

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
        bytes_string = lemma_string.encode('utf8')
        lemma = self.strings.intern(bytes_string, len(bytes_string)).i
        return lemma

    def load_morph_exceptions(self, dict exc):
        cdef unicode pos_str
        cdef unicode form_str
        cdef unicode lemma_str
        cdef dict entries
        cdef dict props
        cdef int lemma
        cdef id_t orth
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


cdef int fill_context(atom_t* context, const int i, const TokenC* tokens) except -1:
    _fill_from_token(&context[P2_orth], &tokens[i-2])
    _fill_from_token(&context[P1_orth], &tokens[i-1])
    _fill_from_token(&context[W_orth], &tokens[i])
    _fill_from_token(&context[N1_orth], &tokens[i+1])
    _fill_from_token(&context[N2_orth], &tokens[i+2])


cdef inline void _fill_from_token(atom_t* context, const TokenC* t) nogil:
    context[0] = t.lex.lower
    context[1] = t.lex.cluster
    context[2] = t.lex.shape
    context[3] = t.lex.prefix
    context[4] = t.lex.suffix
    context[5] = t.tag
    context[6] = t.lemma
    if t.lex.flags & (1 << IS_ALPHA):
        context[7] = 1
    elif t.lex.flags & (1 << IS_PUNCT):
        context[7] = 2
    elif t.lex.flags & (1 << LIKE_URL):
        context[7] = 3
    elif t.lex.flags & (1 << LIKE_NUM):
        context[7] = 4
    else:
        context[7] = 0
