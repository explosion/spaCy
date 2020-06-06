from cymem.cymem cimport Pool
from .transition_system cimport Transition
from ..typedefs cimport attr_t


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
    cdef readonly object orig

    cdef int length
    cdef public int loss
    cdef public list words
    cdef public list tags
    cdef public list pos
    cdef public list morphs
    cdef public list lemmas
    cdef public list sent_starts
    cdef public list heads
    cdef public list labels
    cdef public dict orths
    cdef public list ner
    cdef public dict brackets
    cdef public dict cats
    cdef public dict links

    cdef readonly list cand_to_gold
    cdef readonly list gold_to_cand
