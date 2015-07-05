from libc.string cimport memcpy
from libc.math cimport exp

from cymem.cymem cimport Pool

from thinc.learner cimport LinearModel
from thinc.features cimport Extractor, Feature

from thinc.typedefs cimport atom_t, weight_t, feat_t
cimport cython


from .typedefs cimport flags_t
from .structs cimport TokenC
from .strings cimport StringStore
from .tokens cimport Tokens
from .senses cimport N_SENSES, encode_sense_strs
from .senses cimport NO_SENSE, N_Tops, J_all, J_pert, A_all, J_ppl, V_body
from .gold cimport GoldParse
from .parts_of_speech cimport NOUN, VERB, ADV, ADJ, N_UNIV_TAGS

from . cimport parts_of_speech

from os import path
import json



cdef enum:
    P2W
    P2p
    P2c
    P2c6
    P2c4

    P1W
    P1p
    P1c
    P1c6
    P1c4

    N0W
    N0p
    N0c
    N0c6
    N0c4
    
    N1W
    N1p
    N1c
    N1c6
    N1c4
    
    N2W
    N2p
    N2c
    N2c6
    N2c4

    P1s
    P2s
    
    CONTEXT_SIZE


unigrams = (
    (P2W,),
    (P2p,),
    (P2W, P2p),
    (P2c, P2p),
    (P2c6, P2p),
    (P2c4, P2p),
    (P2c,),

    (P1W,),
    (P1p,),
    (P1W, P1p),
    (P1c, P1p),
    (P1c6, P1p),
    (P1c4, P1p),
    (P1c,),
    (P1W,),
    (P1p,),
    (P1W, P1p),
    (P1c, P1p),
    (P1c6, P1p),
    (P1c4, P1p),
    (P1c,),
    
    (N0p,),
    (N0c, N0p),
    (N0c6, N0p),
    (N0c4, N0p),
    (N0c,),
    (N0p,),
    (N0c, N0p),
    (N0c6, N0p),
    (N0c4, N0p),
    (N0c,),

    (N1p,),
    (N1W, N1p),
    (N1c, N1p),
    (N1c6, N1p),
    (N1c4, N1p),
    (N1c,),
    (N1W,),
    (N1p,),
    (N1W, N1p),
    (N1c, N1p),
    (N1c6, N1p),
    (N1c4, N1p),
    (N1c,),

    (N2p,),
    (N2W, N2p),
    (N2c, N2p),
    (N2c6, N2p),
    (N2c4, N2p),
    (N2c,),
    (N2W,),
    (N2p,),
    (N2W, N2p),
    (N2c, N2p),
    (N2c6, N2p),
    (N2c4, N2p),
    (N2c,),

    (P1s,),
    (P2s,),
    (P1s, P2s,),
    (P1s, N0p),
    (P1s, P2s, N0c),
)


bigrams = (
    (P2p, P1p),
    (P2W, N0p),
    (P2c, P1p),
    (P1c, N0p),
    (P1c6, N0p),

    (N0p, N1p,),
)


trigrams = (
    (P1p, N0p, N1p),
    (P2p, P1p,),
    (P2c4, P1c4, N0c4),
    
    (P1p, N0p, N1p),
    (P1p, N0p,),
    (P1c4, N0c4, N1c4),

    (N0p, N1p, N2p),
    (N0p, N1p,),
    (N0c4, N1c4, N2c4),
)


cdef int fill_token(atom_t* ctxt, const TokenC* token) except -1:
    ctxt[0] = token.lemma
    ctxt[1] = token.tag
    ctxt[2] = token.lex.cluster
    ctxt[3] = token.lex.cluster & 15
    ctxt[4] = token.lex.cluster & 63


cdef int fill_context(atom_t* ctxt, const TokenC* token) except -1:
    # NB: we have padding to keep us safe here
    # See tokens.pyx
    fill_token(&ctxt[P2W], token - 2)
    fill_token(&ctxt[P1W], token - 1)

    fill_token(&ctxt[N0W], token)
    ctxt[N0W] = 0 # Important! Don't condition on this

    fill_token(&ctxt[N1W], token + 1)
    fill_token(&ctxt[N2W], token + 2)
    ctxt[P1s] = (token - 1).sense
    ctxt[P2s] = (token - 2).sense


cdef class FeatureVector:
    cdef Pool mem
    cdef Feature* c
    cdef list extractors
    cdef int length
    cdef int _max_length

    def __init__(self, length=100):
        self.mem = Pool()
        self.c = <Feature*>self.mem.alloc(length, sizeof(Feature))
        self.length = 0
        self._max_length = length

    def __len__(self):
        return self.length

    cpdef int add(self, feat_t key, weight_t value) except -1:
        if self.length == self._max_length:
            self._max_length *= 2
            self.c = <Feature*>self.mem.realloc(self.c, self._max_length * sizeof(Feature))

        self.c[self.length] = Feature(i=0, key=key, value=value)
        self.length += 1

    cdef int extend(self, const Feature* new_feats, int n_feats) except -1:
        new_length = self.length + n_feats
        if new_length >= self._max_length:
            self._max_length = 2 * new_length
            self.c = <Feature*>self.mem.realloc(self.c, new_length * sizeof(Feature))
        memcpy(&self.c[self.length], new_feats, n_feats * sizeof(Feature))
        self.length += n_feats

    def clear(self):
        self.length = 0


cdef class SenseTagger:
    cdef readonly StringStore strings
    cdef readonly LinearModel model
    cdef readonly Extractor extractor
    cdef readonly model_dir
    cdef readonly flags_t[<int>N_UNIV_TAGS] pos_senses
    cdef dict tagdict

    def __init__(self, StringStore strings, model_dir):
        if model_dir is not None and path.isdir(model_dir):
            model_dir = path.join(model_dir, 'wsd')
            
        self.model_dir = model_dir
        if path.exists(path.join(model_dir, 'supersenses.json')):
            self.tagdict = json.load(open(path.join(model_dir, 'supersenses.json')))
        else:
            self.tagdict = {}

        templates = unigrams + bigrams + trigrams
        self.extractor = Extractor(templates)
        self.model = LinearModel(N_SENSES, self.extractor.n_templ)

        model_loc = path.join(self.model_dir, 'model')
        if model_loc and path.exists(model_loc):
            self.model.load(model_loc, freq_thresh=0)
        self.strings = strings

        self.pos_senses[<int>parts_of_speech.NO_TAG] = 0
        self.pos_senses[<int>parts_of_speech.ADJ] = 0
        self.pos_senses[<int>parts_of_speech.ADV] = 0
        self.pos_senses[<int>parts_of_speech.ADP] = 0
        self.pos_senses[<int>parts_of_speech.CONJ] = 0
        self.pos_senses[<int>parts_of_speech.DET] = 0
        self.pos_senses[<int>parts_of_speech.NOUN] = 0
        self.pos_senses[<int>parts_of_speech.NUM] = 0
        self.pos_senses[<int>parts_of_speech.PRON] = 0
        self.pos_senses[<int>parts_of_speech.PRT] = 0
        self.pos_senses[<int>parts_of_speech.VERB] = 0
        self.pos_senses[<int>parts_of_speech.X] = 0
        self.pos_senses[<int>parts_of_speech.PUNCT] = 0
        self.pos_senses[<int>parts_of_speech.EOL] = 0

        cdef flags_t sense = 0
        cdef flags_t one = 1
        for sense in range(N_Tops, V_body):
            self.pos_senses[<int>parts_of_speech.NOUN] |= one << sense

        for sense in range(V_body, J_ppl):
            self.pos_senses[<int>parts_of_speech.VERB] |= one << sense

        self.pos_senses[<int>parts_of_speech.ADV] |= one << A_all
        self.pos_senses[<int>parts_of_speech.ADJ] |= one << J_all
        self.pos_senses[<int>parts_of_speech.ADJ] |= one << J_pert
        self.pos_senses[<int>parts_of_speech.ADJ] |= one << J_ppl

    def __call__(self, Tokens tokens):
        cdef atom_t[CONTEXT_SIZE] local_context
        cdef int i, guess, n_feats
        cdef flags_t valid_senses = 0
        cdef TokenC* token
        cdef flags_t one = 1
        cdef FeatureVector features = FeatureVector(100)
        for i in range(tokens.length):
            token = &tokens.data[i]
            valid_senses = token.lex.senses & self.pos_senses[<int>token.pos]
            if valid_senses >= 2:
                fill_context(local_context, token)
                local_feats = self.extractor.get_feats(local_context, &n_feats)
                features.extend(local_feats, n_feats)
                scores = self.model.get_scores(features.c, features.length)
                self.weight_scores_by_tagdict(<weight_t*><void*>scores, token, 1.0)
                tokens.data[i].sense = self.best_in_set(scores, valid_senses)
                features.clear()

    def train(self, Tokens tokens):
        cdef int i, j
        cdef TokenC* token
        cdef atom_t[CONTEXT_SIZE] context
        cdef int n_feats
        cdef feat_t f_key
        cdef flags_t best_senses = 0
        cdef int f_i
        cdef int cost = 0
        for i in range(tokens.length):
            token = &tokens.data[i]
            pos_senses = self.pos_senses[<int>token.pos]
            lex_senses = token.lex.senses & pos_senses
            if pos_senses >= 2 and lex_senses >= 2:
                fill_context(context, token)
                feats = self.extractor.get_feats(context, &n_feats)
                scores = self.model.get_scores(feats, n_feats)
                #self.weight_scores_by_tagdict(<weight_t*><void*>scores, token, 0.1)
                guess = self.best_in_set(scores, pos_senses)
                best  = self.best_in_set(scores, lex_senses)
                guess_counts = {}
                gold_counts = {}
                if guess != best:
                    cost += 1
                    for j in range(n_feats):
                        f_key = feats[j].key
                        f_i = feats[j].i
                        feat = (f_i, f_key)
                        gold_counts[feat]  = gold_counts.get(feat, 0) + 1.0
                        guess_counts[feat] = guess_counts.get(feat, 0) - 1.0
                self.model.update({guess: guess_counts, best: gold_counts})
        return cost

    cdef int best_in_set(self, const weight_t* scores, flags_t senses) except -1:
        cdef weight_t max_ = 0
        cdef int argmax = -1
        cdef flags_t i
        cdef flags_t one = 1
        for i in range(N_SENSES):
            if (senses & (one << i)) and (argmax == -1 or scores[i] > max_):
                max_ = scores[i]
                argmax = i
        assert argmax >= 0
        return argmax

    @cython.cdivision(True)
    cdef int weight_scores_by_tagdict(self, weight_t* scores, const TokenC* token,
                                      weight_t a) except -1:
        lemma = self.strings[token.lemma]
        if token.pos == NOUN:
            key = lemma + '/n'
        elif token.pos == VERB:
            key = lemma + '/v'
        elif token.pos == ADJ:
            key = lemma + '/j'
        elif token.pos == ADV:
            key = lemma + '/a'
        else:
            return 0

        # First softmax the scores
        cdef int i
        cdef double total = 0
        for i in range(N_SENSES):
            total += exp(scores[i])
        for i in range(N_SENSES):
            scores[i] = <weight_t>(exp(scores[i]) / total)

        probs = self.tagdict.get(key, {})
        for i in range(1, N_SENSES):
            prob = probs.get(str(i-1), 0)
            scores[i] = (a * prob) + ((1 - a) * scores[i])

    def end_training(self):
        self.model.end_training()
        self.model.dump(path.join(self.model_dir, 'model'), freq_thresh=0)

cdef list _set_bits(flags_t flags):
    bits = []
    cdef flags_t bit
    cdef flags_t one = 1
    for bit in range(N_SENSES):
        if flags & (one << bit):
            bits.append(bit)
    return bits
