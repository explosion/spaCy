"""
Fill an array, context, with every _atomic_ value our features reference.
We then write the _actual features_ as tuples of the atoms. The machinery
that translates from the tuples to feature-extractors (which pick the values
out of "context") is in features/extractor.pyx

The atomic feature names are listed in a big enum, so that the feature tuples
can refer to them.
"""
from libc.string cimport memset

from itertools import combinations

from ..structs cimport TokenC

from .stateclass cimport StateClass
from ._state cimport StateC

from cymem.cymem cimport Pool


cdef inline void fill_token(atom_t* context, const TokenC* token) nogil:
    if token is NULL:
        context[0] = 0
        context[1] = 0
        context[2] = 0
        context[3] = 0
        context[4] = 0
        context[5] = 0
        context[6] = 0
        context[7] = 0
        context[8] = 0
        context[9] = 0
        context[10] = 0
        context[11] = 0
        context[12] = 0
    else:
        context[0] = token.lex.orth
        context[1] = token.lemma
        context[2] = token.tag
        context[3] = token.lex.cluster
        # We've read in the string little-endian, so now we can take & (2**n)-1
        # to get the first n bits of the cluster.
        # e.g. s = "1110010101"
        # s = ''.join(reversed(s))
        # first_4_bits = int(s, 2)
        # print first_4_bits
        # 5
        # print "{0:b}".format(prefix).ljust(4, '0')
        # 1110
        # What we're doing here is picking a number where all bits are 1, e.g.
        # 15 is 1111, 63 is 111111 and doing bitwise AND, so getting all bits in
        # the source that are set to 1.
        context[4] = token.lex.cluster & 15
        context[5] = token.lex.cluster & 63
        context[6] = token.dep if token.head != 0 else 0
        context[7] = token.lex.prefix
        context[8] = token.lex.suffix
        context[9] = token.lex.shape
        context[10] = token.ent_iob
        context[11] = token.ent_type

cdef int fill_context(atom_t* ctxt, const StateC* st) nogil:
    # Take care to fill every element of context!
    # We could memset, but this makes it very easy to have broken features that
    # make almost no impact on accuracy. If instead they're unset, the impact
    # tends to be dramatic, so we get an obvious regression to fix...
    fill_token(&ctxt[S2w], st.S_(2))
    fill_token(&ctxt[S1w], st.S_(1))
    fill_token(&ctxt[S1rw], st.R_(st.S(1), 1))
    fill_token(&ctxt[S0lw], st.L_(st.S(0), 1))
    fill_token(&ctxt[S0l2w], st.L_(st.S(0), 2))
    fill_token(&ctxt[S0w], st.S_(0))
    fill_token(&ctxt[S0r2w], st.R_(st.S(0), 2))
    fill_token(&ctxt[S0rw], st.R_(st.S(0), 1))
    fill_token(&ctxt[N0lw], st.L_(st.B(0), 1))
    fill_token(&ctxt[N0l2w], st.L_(st.B(0), 2))
    fill_token(&ctxt[N0w], st.B_(0))
    fill_token(&ctxt[N1w], st.B_(1))
    fill_token(&ctxt[N2w], st.B_(2))
    fill_token(&ctxt[P1w], st.safe_get(st.B(0)-1))
    fill_token(&ctxt[P2w], st.safe_get(st.B(0)-2))

    fill_token(&ctxt[E0w], st.E_(0))
    fill_token(&ctxt[E1w], st.E_(1))

    if st.stack_depth() >= 1 and not st.eol():
        ctxt[dist] = min_(st.B(0) - st.E(0), 5)
    else:
        ctxt[dist] = 0
    ctxt[N0lv] = min_(st.n_L(st.B(0)), 5)
    ctxt[S0lv] = min_(st.n_L(st.S(0)), 5)
    ctxt[S0rv] = min_(st.n_R(st.S(0)), 5)
    ctxt[S1lv] = min_(st.n_L(st.S(1)), 5)
    ctxt[S1rv] = min_(st.n_R(st.S(1)), 5)

    ctxt[S0_has_head] = 0
    ctxt[S1_has_head] = 0
    ctxt[S2_has_head] = 0
    if st.stack_depth() >= 1:
        ctxt[S0_has_head] = st.has_head(st.S(0)) + 1
        if st.stack_depth() >= 2:
            ctxt[S1_has_head] = st.has_head(st.S(1)) + 1
            if st.stack_depth() >= 3:
                ctxt[S2_has_head] = st.has_head(st.S(2)) + 1


cdef inline int min_(int a, int b) nogil:
    return a if a > b else b


ner = (
    (N0W,),
    (P1W,),
    (N1W,),
    (P2W,),
    (N2W,),

    (P1W, N0W,),
    (N0W, N1W),

    (N0_prefix,),
    (N0_suffix,),

    (P1_shape,),
    (N0_shape,),
    (N1_shape,),
    (P1_shape, N0_shape,),
    (N0_shape, P1_shape,),
    (P1_shape, N0_shape, N1_shape),
    (N2_shape,),
    (P2_shape,),

    #(P2_norm, P1_norm, W_norm),
    #(P1_norm, W_norm, N1_norm),
    #(W_norm, N1_norm, N2_norm)

    (P2p,),
    (P1p,),
    (N0p,),
    (N1p,),
    (N2p,),

    (P1p, N0p),
    (N0p, N1p),
    (P2p, P1p, N0p),
    (P1p, N0p, N1p),
    (N0p, N1p, N2p),

    (P2c,),
    (P1c,),
    (N0c,),
    (N1c,),
    (N2c,),

    (P1c, N0c),
    (N0c, N1c),

    (E0W,),
    (E0c,),
    (E0p,),

    (E0W, N0W),
    (E0c, N0W),
    (E0p, N0W),

    (E0p, P1p, N0p),
    (E0c, P1c, N0c),

    (E0w, P1c),
    (E0p, P1p),
    (E0c, P1c),
    (E0p, E1p),
    (E0c, P1p),

    (E1W,),
    (E1c,),
    (E1p,),

    (E0W, E1W),
    (E0W, E1p,),
    (E0p, E1W,),
    (E0p, E1W),

    (P1_ne_iob,),
    (P1_ne_iob, P1_ne_type),
    (N0w, P1_ne_iob, P1_ne_type),

    (N0_shape,),
    (N1_shape,),
    (N2_shape,),
    (P1_shape,),
    (P2_shape,),

    (N0_prefix,),
    (N0_suffix,),

    (P1_ne_iob,),
    (P2_ne_iob,),
    (P1_ne_iob, P2_ne_iob),
    (P1_ne_iob, P1_ne_type),
    (P2_ne_iob, P2_ne_type),
    (N0w, P1_ne_iob, P1_ne_type),

    (N0w, N1w),
)


unigrams = (
    (S2W, S2p),
    (S2c6, S2p),

    (S1W, S1p),
    (S1c6, S1p),

    (S0W, S0p),
    (S0c6, S0p),

    (N0W, N0p),
    (N0p,),
    (N0c,),
    (N0c6, N0p),
    (N0L,),

    (N1W, N1p),
    (N1c6, N1p),

    (N2W, N2p),
    (N2c6, N2p),

    (S0r2W, S0r2p),
    (S0r2c6, S0r2p),
    (S0r2L,),

    (S0rW, S0rp),
    (S0rc6, S0rp),
    (S0rL,),

    (S0l2W, S0l2p),
    (S0l2c6, S0l2p),
    (S0l2L,),

    (S0lW, S0lp),
    (S0lc6, S0lp),
    (S0lL,),

    (N0l2W, N0l2p),
    (N0l2c6, N0l2p),
    (N0l2L,),

    (N0lW, N0lp),
    (N0lc6, N0lp),
    (N0lL,),
)


s0_n0 = (
    (S0W, S0p, N0W, N0p),
    (S0c, S0p, N0c, N0p),
    (S0c6, S0p, N0c6, N0p),
    (S0c4, S0p, N0c4, N0p),
    (S0p, N0p),
    (S0W, N0p),
    (S0p, N0W),
    (S0W, N0c),
    (S0c, N0W),
    (S0p, N0c),
    (S0c, N0p),
    (S0W, S0rp, N0p),
    (S0p, S0rp, N0p),
    (S0p, N0lp, N0W),
    (S0p, N0lp, N0p),
    (S0L, N0p),
    (S0p, S0rL, N0p),
    (S0p, N0lL, N0p),
    (S0p, S0rv, N0p),
    (S0p, N0lv, N0p),
    (S0c6, S0rL, S0r2L, N0p),
    (S0p, N0lL, N0l2L, N0p),
)


s1_s0 = (
    (S1p, S0p),
    (S1p, S0p, S0_has_head),
    (S1W, S0p),
    (S1W, S0p, S0_has_head),
    (S1c, S0p),
    (S1c, S0p, S0_has_head),
    (S1p, S1rL, S0p),
    (S1p, S1rL, S0p, S0_has_head),
    (S1p, S0lL, S0p),
    (S1p, S0lL, S0p, S0_has_head),
    (S1p, S0lL, S0l2L, S0p),
    (S1p, S0lL, S0l2L, S0p, S0_has_head),
    (S1L, S0L, S0W),
    (S1L, S0L, S0p),
    (S1p, S1L, S0L, S0p),
    (S1p, S0p),
)


s1_n0 = (
    (S1p, N0p),
    (S1c, N0c),
    (S1c, N0p),
    (S1p, N0c),
    (S1W, S1p, N0p),
    (S1p, N0W, N0p),
    (S1c6, S1p, N0c6, N0p),
    (S1L, N0p),
    (S1p, S1rL, N0p),
    (S1p, S1rp, N0p),
)


s0_n1 = (
    (S0p, N1p),
    (S0c, N1c),
    (S0c, N1p),
    (S0p, N1c),
    (S0W, S0p, N1p),
    (S0p, N1W, N1p),
    (S0c6, S0p, N1c6, N1p),
    (S0L, N1p),
    (S0p, S0rL, N1p),
)


n0_n1 = (
    (N0W, N0p, N1W, N1p),
    (N0W, N0p, N1p),
    (N0p, N1W, N1p),
    (N0c, N0p, N1c, N1p),
    (N0c6, N0p, N1c6, N1p),
    (N0c, N1c),
    (N0p, N1c),
)

tree_shape = (
    (dist,),
    (S0p, S0_has_head, S1_has_head, S2_has_head),
    (S0p, S0lv, S0rv),
    (N0p, N0lv),
)

trigrams = (
    (N0p, N1p, N2p),
    (S0p, S0lp, S0l2p),
    (S0p, S0rp, S0r2p),
    (S0p, S1p, S2p),
    (S1p, S0p, N0p),
    (S0p, S0lp, N0p),
    (S0p, N0p, N0lp),
    (N0p, N0lp, N0l2p),

    (S0W, S0p, S0rL, S0r2L),
    (S0p, S0rL, S0r2L),

    (S0W, S0p, S0lL, S0l2L),
    (S0p, S0lL, S0l2L),

    (N0W, N0p, N0lL, N0l2L),
    (N0p, N0lL, N0l2L),
)


words = (
    S2w,
    S1w,
    S1rw,
    S0lw,
    S0l2w,
    S0w,
    S0r2w,
    S0rw,
    N0lw,
    N0l2w,
    N0w,
    N1w,
    N2w,
    P1w,
    P2w
)

tags = (
    S2p,
    S1p,
    S1rp,
    S0lp,
    S0l2p,
    S0p,
    S0r2p,
    S0rp,
    N0lp,
    N0l2p,
    N0p,
    N1p,
    N2p,
    P1p,
    P2p
)

labels = (
    S2L,
    S1L,
    S1rL,
    S0lL,
    S0l2L,
    S0L,
    S0r2L,
    S0rL,
    N0lL,
    N0l2L,
    N0L,
    N1L,
    N2L,
    P1L,
    P2L
)
