from libc.stdint cimport uint8_t

from cymem.cymem cimport Pool

from thinc.learner cimport LinearModel
from thinc.features cimport Extractor
from thinc.typedefs cimport atom_t, feat_t, weight_t, class_t

from preshed.maps cimport PreshMapArray

from .typedefs cimport hash_t
from .tokens cimport Tokens, Morphology


# Google universal tag set
cdef enum univ_tag_t:
    NO_TAG
    ADJ
    ADV
    ADP
    CONJ
    DET
    NOUN
    NUM
    PRON
    PRT
    VERB
    X
    PUNCT
    EOL
    N_UNIV_TAGS


cdef struct PosTag:
    Morphology morph
    int id
    univ_tag_t pos


cdef class Tagger:
    cdef class_t predict(self, const atom_t* context, object golds=*) except *
 
    cpdef readonly Pool mem
    cpdef readonly Extractor extractor
    cpdef readonly LinearModel model

    cpdef readonly list tag_names
    cdef PosTag* tags
    cdef dict tagdict
