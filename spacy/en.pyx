# cython: profile=True
# cython: embedsignature=True
'''Tokenize English text, using a scheme that differs from the Penn Treebank 3
scheme in several important respects:

* Whitespace is added as tokens, except for single spaces. e.g.,

    >>> [w.string for w in EN.tokenize(u'\\nHello  \\tThere')]
    [u'\\n', u'Hello', u' ', u'\\t', u'There']

* Contractions are normalized, e.g.

    >>> [w.string for w in EN.tokenize(u"isn't ain't won't he's")]
    [u'is', u'not', u'are', u'not', u'will', u'not', u'he', u"__s"]
  
* Hyphenated words are split, with the hyphen preserved, e.g.:
    
    >>> [w.string for w in EN.tokenize(u'New York-based')]
    [u'New', u'York', u'-', u'based']

Other improvements:

* Email addresses, URLs, European-formatted dates and other numeric entities not
  found in the PTB are tokenized correctly
* Heuristic handling of word-final periods (PTB expects sentence boundary detection
  as a pre-process before tokenization.)

Take care to ensure your training and run-time data is tokenized according to the
same scheme. Tokenization problems are a major cause of poor performance for
NLP tools. If you're using a pre-trained model, the :py:mod:`spacy.ptb3` module
provides a fully Penn Treebank 3-compliant tokenizer.
'''
from __future__ import unicode_literals

cimport lang
from .typedefs cimport flags_t
import orth
from .morphology cimport NO_TAG, ADJ, ADV, ADP, CONJ, DET, NOUN, NUM, PRON, PRT, VERB
from .morphology cimport X, PUNCT, EOL

from .tokens cimport Morphology


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
    (P1_sic,),
    (N1_sic,),
    (N2_sic,),
    (P2_sic,),

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
)


cdef class English(Language):
    """English tokenizer, tightly coupled to lexicon.

    Attributes:
        name (unicode): The two letter code used by Wikipedia for the language.
        lexicon (Lexicon): The lexicon. Exposes the lookup method.
    """
    def get_props(self, unicode string):
        return {'flags': self.set_flags(string), 'dense': orth.word_shape(string)}

    def set_flags(self, unicode string):
        cdef flags_t flags = 0
        flags |= orth.is_alpha(string) << IS_ALPHA
        flags |= orth.is_ascii(string) << IS_ASCII
        flags |= orth.is_digit(string) << IS_DIGIT
        flags |= orth.is_lower(string) << IS_LOWER
        flags |= orth.is_punct(string) << IS_PUNCT
        flags |= orth.is_space(string) << IS_SPACE
        flags |= orth.is_title(string) << IS_TITLE
        flags |= orth.is_upper(string) << IS_UPPER

        flags |= orth.like_url(string) << LIKE_URL
        flags |= orth.like_number(string) << LIKE_NUMBER
        return flags

    def set_pos(self, Tokens tokens):
        cdef int i
        cdef atom_t[N_CONTEXT_FIELDS] context
        cdef TokenC* t = tokens.data
        assert self.morphologizer is not None
        cdef dict tagdict = self.pos_tagger.tagdict
        for i in range(tokens.length):
            if t[i].lex.sic in tagdict:
                t[i].pos = tagdict[t[i].lex.sic]
            else:
                fill_pos_context(context, i, t)
                t[i].pos = self.pos_tagger.predict(context)
                self.morphologizer.set_morph(i, t)

    def train_pos(self, Tokens tokens, golds):
        cdef int i
        cdef atom_t[N_CONTEXT_FIELDS] context
        c = 0
        cdef TokenC* t = tokens.data
        for i in range(tokens.length):
            fill_pos_context(context, i, t)
            t[i].pos = self.pos_tagger.predict(context, [golds[i]])
            self.morphologizer.set_morph(i, t)
            c += t[i].pos == golds[i]
        return c


cdef int fill_pos_context(atom_t* context, const int i, const TokenC* tokens) except -1:
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
    context[6] = t.sense


EN = English('en')
