from .lexeme cimport *

from thinc.typedefs cimport atom_t


TEMPLATES = (
    (N0i,),
    (N0w,),
    (N0suff,),
    (N0pref,),
    (P1t,),
    (P2t,),
    (P1t, P2t),
    (P1t, N0w),
    (P1w,),
    (P1suff,),
    (P2w,),
    (N1w,),
    (N1suff,),
    (N2w,),

    (N0shape,),
    (N0c,),
    (N1c,),
    (N2c,),
    (P1c,),
    (P2c,),
    (P1c, N0c),
    (N0c, N1c),
    (P1c, P1t),
    (P1c, P1t, N0c),
    (P1t, N0c),
    (N0oft_upper,),
    (N0oft_title,),

    (P1w, N0w),
    (N0w, N1w),

    (N0pos,),
    (P1t, N0pos, N1pos),
    (P1t, N1pos),

    (N0url,),
    (N0num,),
    (P1url,),
    (P1url,),
    (N1num,),
    (N1url,),
)


cdef int fill_context(atom_t* context, int i, Tokens tokens) except -1:
    _fill_token(&context[P2i], tokens.lex[i-2])
    _fill_token(&context[P1i], tokens.lex[i-1])
    _fill_token(&context[N0i], tokens.lex[i])
    _fill_token(&context[N1i], tokens.lex[i+1])
    _fill_token(&context[N2i], tokens.lex[i+2])
    context[P1t] = tokens.pos[i-1]
    context[P2t] = tokens.pos[i-2]


cdef inline void _fill_token(atom_t* atoms, Lexeme* lex) nogil:
    atoms[0] = lex.sic
    atoms[1] = lex.cluster
    atoms[2] = lex.norm if (lex.prob != 0 and lex.prob >= -10) else lex.shape
    atoms[3] = lex.shape
    atoms[4] = lex.prefix
    atoms[5] = lex.suffix

    atoms[6] = lex.flags & (1 << IS_TITLE)
    atoms[7] = lex.flags & (1 << IS_UPPER)
    atoms[8] = lex.flags & (1 << OFT_TITLE)
    atoms[9] = lex.flags & (1 << OFT_UPPER)
    atoms[10] = lex.postype
    atoms[11] = lex.flags & (1 << LIKE_URL)
    atoms[12] = lex.flags & (1 << LIKE_NUMBER)

