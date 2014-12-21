from os import path
from thinc.typedefs cimport atom_t

from ..typedefs cimport NO_TAG, ADJ, ADV, ADP, CONJ, DET, NOUN, NUM, PRON, PRT, VERB
from ..typedefs cimport X, PUNCT, EOL
from ..structs cimport TokenC, Morphology
from ..tokens cimport Tokens


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


cdef class EnPosTagger(Tagger):
    def __init__(self, data_dir, morphologizer):
        model_dir = path.join(data_dir, 'pos')
        Tagger.__init__(self, path.join(model_dir))
        self.morphologizer = morphologizer

    def __call__(self, Tokens tokens):
        cdef int i
        cdef atom_t[N_CONTEXT_FIELDS] context
        cdef TokenC* t = tokens.data
        assert self.morphologizer is not None
        for i in range(tokens.length):
            fill_context(context, i, t)
            t[i].pos = self.predict(context)
            self.morphologizer.set_morph(i, t)

    def train(self, Tokens tokens, golds):
        cdef int i
        cdef atom_t[N_CONTEXT_FIELDS] context
        c = 0
        cdef TokenC* t = tokens.data
        for i in range(tokens.length):
            fill_context(context, i, t)
            t[i].pos = self.predict(context, [golds[i]])
            self.morphologizer.set_morph(i, t)
            c += t[i].pos == golds[i]
        return c


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
