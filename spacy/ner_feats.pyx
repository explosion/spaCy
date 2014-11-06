from spacy.context cimport FIELD_IDS, Token


cdef Token P4 = FIELD_IDS.P4
cdef Token P3 = FIELD_IDS.P3
cdef Token P2 = FIELD_IDS.P2
cdef Token P1 = FIELD_IDS.P1
cdef Token N0 = FIELD_IDS.N0
cdef Token N1 = FIELD_IDS.N1
cdef Token N2 = FIELD_IDS.N2
cdef Token N3 = FIELD_IDS.N3
cdef Token N4 = FIELD_IDS.N4

"""
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

    (P2.pos, P1.pos, N0.sic),
    (N0.sic, N1.pos, N2.pos)
)
"""

LOCAL = (
    (N0.sic,),
    (P1.sic,),
    (N1.sic,),
    (P2.sic,),
    (N2.sic,),
    (P3.sic,),
    (N3.sic,),
    (P4.sic,),
    (N4.sic,),
    
    (P1.sic, N0.sic,),
    (N0.sic, N1.sic),
    
    (N0.prefix,),
    (N0.suffix,),

    (P1.shape,),
    (N0.shape,),
    (N1.shape,),
    (P1.shape, N0.shape,),
    (N0.shape, P1.shape,),
    (P1.shape, N0.shape, N1.shape),
    (N2.shape,),
    (P2.shape,),
    (P3.shape,),
    (N3.shape,),
    (P4.shape,),
    (N4.shape,),

    (P2.norm, P1.norm, N0.norm),
    (P1.norm, N0.norm, N1.norm),
    (N0.norm, N1.norm, N2.norm)
)

BOOLS = (
    (N0.is_title,),
)


HISTORY = (
    (P1.ner,),
    (P1.ner, N0.sic,),
    (P2.ner,),
    (P2.ner, P1.ner),
    (P2.ner, P1.ner, N0.sic),
    (P2.pos, P1.ner, N0.pos),
    (P2.ner, P1.pos, N0.pos),
    (P3.ner,),
    (P4.ner,),
)

POS = (
    (P4.pos,),
    (P3.pos,),
    (P2.pos,),
    (P1.pos,),
    (N0.pos,),
    (N1.pos,),
    (N2.pos,),
    (N3.pos,),
    (N4.pos,),

    (P1.pos, N0.pos),
    (N0.pos, N1.pos),
    (P2.pos, P1.pos, N0.pos),
    (P1.pos, N0.pos, N1.pos),
    (N0.pos, N1.pos, N2.pos)
)

CLUSTERS = (
    (P4.cluster,),
    (P3.cluster,),
    (P2.cluster,),
    (P1.cluster,),
    (N0.cluster,),
    (N1.cluster,),
    (N2.cluster,),
    (N3.cluster,),
    (N4.cluster,),

    (P1.cluster, N0.cluster),
    (N0.cluster, N1.cluster),
)


CLUSTER_POS = (
    (P1.cluster, N0.pos),
    (N0.pos, P1.cluster),
    (N0.cluster, N1.pos),
    (N0.pos, N1.cluster)
)


GAZ = (
    (N0.in_males,),
    (N0.in_females,),
    (N0.in_surnames,),
    (N0.in_places,),
    (N0.in_games,),
    (N0.in_celebs,),
    (N0.in_names,),
    (P1.in_males,),
    (P1.in_females,),
    (P1.in_surnames,),
    (P1.in_places,),
    (P1.in_games,),
    (P1.in_celebs,),
    (P1.in_names,),
    (N1.in_males,),
    (N1.in_females,),
    (N1.in_surnames,),
    (N1.in_places,),
    (N1.in_games,),
    (N1.in_celebs,),
    (N1.in_names,),
)

TEMPLATES = LOCAL + HISTORY + CLUSTERS + POS + CLUSTER_POS + GAZ + BOOLS
