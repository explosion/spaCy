from spacy.context cimport FIELD_IDS, Token


cpdef Token P2 = FIELD_IDS.P2
cpdef Token P1 = FIELD_IDS.P1
cpdef Token N0 = FIELD_IDS.N0
cpdef Token N1 = FIELD_IDS.N1
cpdef Token N2 = FIELD_IDS.N2


TEMPLATES = (
    (N0.i,),
    (N0.w,),
    (N0.suff,),
    (N0.pref,),
    (P1.pos,),
    (P2.pos,),
    (P1.pos, P2.pos),
    (P1.pos, N0.w),
    (P1.w,),
    (P1.suff,),
    (P2.w,),
    (N1.w,),
    (N1.suff,),
    (N2.w,),

    (N0.shape,),
    (N0.c,),
    (N1.c,),
    (N2.c,),
    (P1.c,),
    (P2.c,),
    (N0.oft_upper,),
    (N0.oft_title,),

    (N0.postype,),

    (P1.url,),
    (N1.num,),
    (N1.url,),
)
