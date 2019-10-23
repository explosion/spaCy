from cymem.cymem cimport Pool

from .typedefs cimport attr_t
from .syntax.transition_system cimport Transition


cdef struct GoldParseC:
    int* tags
    int* heads
    int* has_dep
    int* sent_start
    attr_t* labels
    int** brackets
    Transition* ner


cdef class GoldParse:
    cdef Pool mem

    cdef GoldParseC c
    cdef readonly RawAnnot orig

    cdef int length
    cdef public int loss
    cdef public list words
    cdef public list tags
    cdef public list morphology
    cdef public list heads
    cdef public list labels
    cdef public dict orths
    cdef public list ner
    cdef public list ents
    cdef public dict brackets
    cdef public object cats
    cdef public dict links

    cdef readonly list cand_to_gold
    cdef readonly list gold_to_cand
    cdef readonly list orig_annot  # TODO: delete


cdef class RawAnnot:
    cdef readonly list ids
    cdef readonly list words
    cdef readonly list tags
    cdef readonly list heads
    cdef readonly list deps
    cdef readonly list ents

