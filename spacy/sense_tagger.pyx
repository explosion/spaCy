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
 
    Hw
    Hp
    Hc
    Hc6
    Hc4
    
    N3W
    P3W

    P1s
    P2s

   
    CONTEXT_SIZE


unigrams = (
    (Hw,),
    (Hp,),
    (Hw, Hp),
    (Hc, Hp),
    (Hc6, Hp),
    (Hc4, Hp),
    (Hc,),

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

    (N3W,),
    (P3W,),
)


bigrams = (
    (P2p, P1p),
    (P2W, N0p),
    (P2c, P1p),
    (P1c, N0p),
    (P1c6, N0p),

    (N0p, N1p,),
    (P2W, P1W),
    (P1W, N1W),
    (N1W, N2W),
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
    (P1W, N0p, N0W),
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
    fill_token(&ctxt[Hw], token + token.head)
    ctxt[P1s] = (token - 1).sense
    ctxt[P2s] = (token - 2).sense
    ctxt[N3W] = (token + 3).lemma
    ctxt[P3W] = (token - 3).lemma


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
        self.model_dir = model_dir
        if path.exists(path.join(model_dir, 'wordnet', 'supersenses.json')):
            self.tagdict = json.load(open(path.join(model_dir, 'wordnet', 'supersenses.json')))
        else:
            self.tagdict = {}

        if model_dir is not None and path.isdir(model_dir):
            model_dir = path.join(model_dir, 'wsd')

        templates = unigrams + bigrams + trigrams
        self.extractor = Extractor(templates)
        self.model = LinearModel(N_SENSES, self.extractor.n_templ)

        self.strings = strings
        cdef flags_t all_senses = 0
        cdef flags_t sense = 0
        cdef flags_t one = 1
        for sense in range(1, N_SENSES):
            all_senses |= (one << sense)

        self.pos_senses[<int>parts_of_speech.NO_TAG] = all_senses
        self.pos_senses[<int>parts_of_speech.ADJ] = all_senses
        self.pos_senses[<int>parts_of_speech.ADV] = all_senses
        self.pos_senses[<int>parts_of_speech.ADP] = all_senses
        self.pos_senses[<int>parts_of_speech.CONJ] = 0
        self.pos_senses[<int>parts_of_speech.DET] = 0
        self.pos_senses[<int>parts_of_speech.NUM] = 0
        self.pos_senses[<int>parts_of_speech.PRON] = 0
        self.pos_senses[<int>parts_of_speech.PRT] = all_senses
        self.pos_senses[<int>parts_of_speech.X] = all_senses
        self.pos_senses[<int>parts_of_speech.PUNCT] = 0
        self.pos_senses[<int>parts_of_speech.EOL] = 0

        for sense in range(N_Tops, V_body):
            self.pos_senses[<int>parts_of_speech.NOUN] |= one << sense

        self.pos_senses[<int>parts_of_speech.VERB] = 0
        for sense in range(V_body, J_ppl):
            self.pos_senses[<int>parts_of_speech.VERB] |= one << sense

    def __call__(self, Tokens tokens):
        cdef atom_t[CONTEXT_SIZE] local_context
        cdef int i, guess, n_feats
        cdef flags_t valid_senses = 0
        cdef TokenC* token
        cdef flags_t one = 1
        cdef int n_doc_feats
        cdef Pool mem = Pool()
        feats = self.get_doc_feats(mem, tokens, &n_doc_feats)
        for i in range(tokens.length):
            token = &tokens.data[i]
            valid_senses = token.lex.senses & self.pos_senses[<int>token.pos]
            if valid_senses >= 2:
                fill_context(local_context, token)
                n_local_feats = self.extractor.set_feats(&feats[n_doc_feats],
                                                         local_context)
                scores = self.model.get_scores(feats, n_local_feats)
                self.weight_scores_by_tagdict(<weight_t*><void*>scores, token, 0.0)
                tokens.data[i].sense = self.best_in_set(scores, valid_senses)
            else:
                token.sense = NO_SENSE

    def train(self, Tokens tokens):
        cdef int i, j
        cdef TokenC* token
        cdef atom_t[CONTEXT_SIZE] context
        cdef int n_doc_feats, n_local_feats
        cdef feat_t f_key
        cdef flags_t best_senses = 0
        cdef int f_i
        cdef int cost = 0

        cdef Pool mem = Pool()
        feats = self.get_doc_feats(mem, tokens, &n_doc_feats)
        for i in range(tokens.length):
            token = &tokens.data[i]
            pos_senses = self.pos_senses[<int>token.pos]
            lex_senses = token.lex.senses & pos_senses
            if lex_senses >= 2:
                fill_context(context, token)

                n_local_feats = self.extractor.set_feats(&feats[n_doc_feats], context)
                scores = self.model.get_scores(feats, n_doc_feats + n_local_feats)
                guess  = self.best_in_set(scores, pos_senses)
                best   = self.best_in_set(scores, lex_senses)
                update = self._make_update(feats, n_doc_feats + n_local_feats,
                                           guess, best)
                self.model.update(update)
                token.sense = best
                cost += guess != best
            else:
                token.sense = 1
        return cost

    cdef dict _make_update(self, const Feature* feats, int n_feats, int guess, int best):
        guess_counts = {}
        gold_counts = {}
        if guess != best:
            for j in range(n_feats):
                f_key = feats[j].key
                f_i = feats[j].i
                feat = (f_i, f_key)
                gold_counts[feat]  = gold_counts.get(feat, 0) + 1.0
                guess_counts[feat] = guess_counts.get(feat, 0) - 1.0
        return {guess: guess_counts, best: gold_counts}

    cdef Feature* get_doc_feats(self, Pool mem, Tokens tokens, int* n_feats) except NULL:
        # Get features for the document
        # Start with activation strengths for each supersense
        n_feats[0] = N_SENSES
        feats = <Feature*>mem.alloc(n_feats[0] + self.extractor.n_templ + 1,
                                    sizeof(Feature))
        cdef int i, ssense
        for ssense in range(N_SENSES):
            feats[ssense] = Feature(i=0, key=ssense, value=0)
        cdef flags_t pos_senses
        cdef flags_t one = 1
        for i in range(tokens.length):
            sense_probs = self.tagdict.get(tokens.data[i].lemma, {})
            pos_senses = self.pos_senses[<int>tokens.data[i].pos]
            for ssense_str, prob in sense_probs.items():
                ssense = int(ssense_str + 1)
                if pos_senses & (one << <flags_t>ssense):
                    feats[ssense].value += prob
        return feats

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

    cdef int weight_scores_by_tagdict(self, weight_t* scores, const TokenC* token,
                                      weight_t a) except -1:
        lemma = self.strings[token.lemma]

        # First softmax the scores
        softmax(scores, N_SENSES)

        probs = self.tagdict.get(lemma, {})
        for i in range(1, N_SENSES):
            prob = probs.get(unicode(i-1), 0)
            scores[i] = (a * prob) + ((1 - a) * scores[i])

    def end_training(self):
        self.model.end_training()
        self.model.dump(path.join(self.model_dir, 'model'), freq_thresh=0)


@cython.cdivision(True)
cdef void softmax(weight_t* scores, int n_classes) nogil:
    cdef int i
    cdef double total = 0
    for i in range(N_SENSES):
        total += exp(scores[i])
    for i in range(N_SENSES):
        scores[i] = <weight_t>(exp(scores[i]) / total)



cdef list _set_bits(flags_t flags):
    bits = []
    cdef flags_t bit
    cdef flags_t one = 1
    for bit in range(N_SENSES):
        if flags & (one << bit):
            bits.append(bit)
    return bits
