from spacy.context cimport FIELD_IDS, Token


cpdef Token P2 = FIELD_IDS.P2
cpdef Token P1 = FIELD_IDS.P1
cpdef Token N0 = FIELD_IDS.N0
cpdef Token N1 = FIELD_IDS.N1
cpdef Token N2 = FIELD_IDS.N2


TEMPLATES = (
    (N0.sic,),
    (N0.norm,),
    (N0.suffix,),
    (N0.prefix,),
    (P1.pos,),
    (P2.pos,),
    (P1.pos, P2.pos),
    (P1.pos, N0.norm),
    (P1.norm,),
    (P1.suffix,),
    (P2.norm,),
    (N1.norm,),
    (N1.suffix,),
    (N2.norm,),

    (N0.shape,),
    (N0.cluster,),
    (N1.cluster,),
    (N2.cluster,),
    (P1.cluster,),
    (P2.cluster,),
    (N0.oft_upper,),
    (N0.oft_title,),

    (N0.postype,),

    (P1.like_url,),
    (N1.like_number,),
    (N1.like_url,),
)
