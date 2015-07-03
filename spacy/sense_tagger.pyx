from .typedefs cimport flags_t
from .structs cimport TokenC
from .strings cimport StringStore
from .tokens cimport Tokens
from .senses cimport POS_SENSES, N_SENSES, encode_sense_strs
from .gold cimport GoldParse
from .parts_of_speech cimport NOUN, VERB

from thinc.learner cimport LinearModel
from thinc.features cimport Extractor

from thinc.typedefs cimport atom_t, weight_t, feat_t

from os import path



cdef enum:
    P2W
    P2p
    P2c
    P2c6
    P2c4
    P2ss
    P2s

    P1W
    P1p
    P1c
    P1c6
    P1c4
    P1ss
    P1s

    N0W
    N0p
    N0c
    N0c6
    N0c4
    N0ss
    N0s
    
    N1W
    N1p
    N1c
    N1c6
    N1c4
    N1ss
    N1s
    
    N2W
    N2p
    N2c
    N2c6
    N2c4
    N2ss
    N2s
    
    CONTEXT_SIZE


unigrams = (
    (P2W,),
    (P2p,),
    (P2W, P2p),
    (P2c, P2p),
    (P2c6, P2p),
    (P2c4, P2p),
    (P2c,),
    (P2ss,),
    (P1s,),

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
    (P1ss,),
    (P1s,),
    
    (N0p,),
    (N0W, N0p),
    (N0c, N0p),
    (N0c6, N0p),
    (N0c4, N0p),
    (N0c,),
    (N0W,),
    (N0p,),
    (N0W, N0p),
    (N0c, N0p),
    (N0c6, N0p),
    (N0c4, N0p),
    (N0c,),
    (N0ss,),

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
    (N1ss,),

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
    (N2ss,),
)


bigrams = (
    (P2p, P1p),
    (P2W, N0p),
    (P2c, P1p),
    (P1c, N0p),
    (P1c6, N0p),

    (P2s, P1s),
    (P2ss, P1s,),
    (P2ss, P1ss,),

    (P1ss, N0ss),

    (N0p, N1p,),
)


trigrams = (
    (P1p, N0p, N1p),
    (P2p, P1p, N0ss),
    (P2c4, P1c4, N0c4),
    
    (P1p, N0p, N1p),
    (P1p, N0p, N1ss),
    (P1c4, N0c4, N1c4),

    (N0p, N1p, N2p),
    (N0p, N1p, N2ss),
    (N0c4, N1c4, N2c4),
)


cdef int fill_token(atom_t* ctxt, const TokenC* token) except -1:
    ctxt[0] = token.lemma
    ctxt[1] = token.tag
    ctxt[2] = token.lex.cluster
    ctxt[3] = token.lex.cluster & 15
    ctxt[4] = token.lex.cluster & 63
    ctxt[5] = token.lex.senses & POS_SENSES[<int>token.pos]
    ctxt[6] = token.sense


cdef int fill_context(atom_t* ctxt, const TokenC* token) except -1:
    # NB: we have padding to keep us safe here
    # See tokens.pyx
    fill_token(&ctxt[P2W], token - 2)
    fill_token(&ctxt[P1W], token - 1)

    fill_token(&ctxt[N0W], token)
    ctxt[N0W] = 0 # Important! Don't condition on this

    fill_token(&ctxt[N1W], token + 1)
    fill_token(&ctxt[N2W], token + 2)


cdef class SenseTagger:
    cdef readonly StringStore strings
    cdef readonly LinearModel model
    cdef readonly Extractor extractor
    cdef readonly model_dir

    def __init__(self, StringStore strings, model_dir):
        if model_dir is not None and path.isdir(model_dir):
            model_dir = path.join(model_dir, 'model')

        templates = unigrams + bigrams + trigrams
        self.extractor = Extractor(templates)
        self.model = LinearModel(N_SENSES, self.extractor.n_templ)
        self.model_dir = model_dir
        if self.model_dir and path.exists(self.model_dir):
            self.model.load(self.model_dir, freq_thresh=0)
        self.strings = strings

    def __call__(self, Tokens tokens):
        cdef atom_t[CONTEXT_SIZE] context
        cdef int i, guess, n_feats
        cdef const TokenC* token
        for i in range(tokens.length):
            token = &tokens.data[i]
            if token.pos in (NOUN, VERB):
                fill_context(context, token)
                feats = self.extractor.get_feats(context, &n_feats)
                scores = self.model.get_scores(feats, n_feats)
                tokens.data[i].sense = self.best_in_set(scores, POS_SENSES[<int>token.pos])

    def train(self, Tokens tokens, GoldParse gold):
        cdef int i, j
        for i, ssenses in enumerate(gold.ssenses):
            if ssenses:
                gold.c.ssenses[i] = encode_sense_strs(ssenses)
            else:
                gold.c.ssenses[i] = pos_senses(&tokens.data[i])
        
        cdef atom_t[CONTEXT_SIZE] context
        cdef int n_feats
        cdef feat_t f_key
        cdef int f_i
        cdef int cost = 0
        for i in range(tokens.length):
            token = &tokens.data[i]
            if token.pos in (NOUN, VERB) \
            and token.lex.senses >= 2 \
            and gold.c.ssenses[i] >= 2:
                fill_context(context, token)
                feats = self.extractor.get_feats(context, &n_feats)
                scores = self.model.get_scores(feats, n_feats)
                token.sense = self.best_in_set(scores, POS_SENSES[<int>token.pos])
                best = self.best_in_set(scores, gold.c.ssenses[i])
                guess_counts = {}
                gold_counts = {}
                if token.sense != best:
                    for j in range(n_feats):
                        f_key = feats[j].key
                        f_i = feats[j].i
                        feat = (f_i, f_key)
                        gold_counts[feat]  = gold_counts.get(feat, 0) + 1.0
                        guess_counts[feat] = guess_counts.get(feat, 0) - 1.0
                #self.model.update({token.sense: guess_counts, best: gold_counts})
        return cost

    cdef int best_in_set(self, const weight_t* scores, flags_t senses) except -1:
        cdef weight_t max_ = 0
        cdef int argmax = -1
        cdef flags_t i
        for i in range(N_SENSES):
            if (senses & (1 << i)) and (argmax == -1 or scores[i] > max_):
                max_ = scores[i]
                argmax = i
        assert argmax >= 0
        return argmax


cdef flags_t pos_senses(const TokenC* token) nogil:
    return token.lex.senses & POS_SENSES[<int>token.pos]


cdef list _set_bits(flags_t flags):
    bits = []
    cdef flags_t bit
    for bit in range(N_SENSES):
        if flags & (1 << bit):
            bits.append(bit)
    return bits
