from thinc.api cimport Example
from thinc.typedefs cimport atom_t

from .typedefs cimport flags_t
from .structs cimport TokenC
from .strings cimport StringStore
from .tokens cimport Tokens
from ._ml cimport Model
from .senses cimport POS_SENSES, N_SENSES
from .gold cimport GoldParse



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
    fill_token(&ctxt[P2W], token - 2)
    fill_token(&ctxt[P1W], token - 1)

    fill_token(&ctxt[N0W], token)
    ctxt[N0W] = 0 # Important! Don't condition on this

    fill_token(&ctxt[N1W], token + 1)
    fill_token(&ctxt[N2W], token + 2)


cdef class SenseTagger:
    cdef readonly StringStore strings
    cdef readonly Model model

    def __init__(self, StringStore strings, model_dir):
        self.strings = strings
        templates = unigrams + bigrams + trigrams
        self.model = Model(N_SENSES, templates, model_dir)

    def __call__(self, Tokens tokens):
        eg = Example(self.model.n_classes, CONTEXT_SIZE, self.model.n_feats,
                     self.model.n_feats)
        cdef int i
        for i in range(tokens.length):
            n_valid = self._set_valid(<bint*>eg.c.is_valid, pos_senses(&tokens.data[i]))
            if n_valid >= 2:
                fill_context(eg.c.atoms, &tokens.data[i])
                self.model.predict(eg)
                tokens.data[i].sense = eg.c.guess

    def train(self, Tokens tokens, GoldParse gold):
        eg = Example(self.model.n_classes, CONTEXT_SIZE, self.model.n_feats+1,
                     self.model.n_feats+1)
        cdef int i
        cdef int cost = 0
        for i in range(tokens.length):
            if tokens.data[i].lex.senses == 0:
                continue
            self._set_costs(<bint*>eg.c.is_valid, eg.c.costs, pos_senses(&tokens.data[i]))
            fill_context(eg.c.atoms, &tokens.data[i])

            self.model.train(eg)

            tokens.data[i].sense = eg.c.guess
            cost += eg.c.cost
        return cost

    cdef int _set_valid(self, bint* is_valid, flags_t senses) except -1:
        cdef int n_valid
        cdef flags_t bit
        for bit in range(N_SENSES):
            is_valid[bit] = senses & (1 << bit)
            n_valid += is_valid[bit]
        return n_valid

    cdef int _set_costs(self, bint* is_valid, int* costs, flags_t senses):
        cdef flags_t bit
        for bit in range(N_SENSES):
            is_valid[bit] = True
            costs[bit] = 0 if senses & (1 << bit) else 1

cdef flags_t pos_senses(const TokenC* token) nogil:
    return token.lex.senses & POS_SENSES[<int>token.pos]
