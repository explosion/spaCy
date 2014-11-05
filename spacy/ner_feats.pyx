from spacy.context cimport FIELD_IDS, Token


cdef Token P2 = FIELD_IDS.P2
cdef Token P1 = FIELD_IDS.P1
cdef Token N0 = FIELD_IDS.N0
cdef Token N1 = FIELD_IDS.N1
cdef Token N2 = FIELD_IDS.N2


TEMPLATES = (
    (N0.sic,),
    (N0.cluster,),

    (P1.pos,),
    (P1.sic,),

    (N1.norm,),
    (N1.pos,),

    (P1.ner,),
    (P2.ner,),

    (N0.cluster,),
    (P1.cluster,),
    (N1.cluster,),

    (N0.is_alpha,),
    (N0.is_digit,),
    (N0.is_title,),
    (N0.is_upper,),

    (N0.is_title, N0.oft_title),
    (N0.is_upper, N0.oft_upper),

    (P1.cluster, N0.norm),
    (N0.norm, N1.cluster),

    (P1.ner, N0.pos),
    (P2.ner, P1.ner, N0.pos),
)
