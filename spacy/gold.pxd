from cymem.cymem cimport Pool

from spacy.tokens import Doc
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
    cdef readonly TokenAnnotation orig

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


cdef class TokenAnnotation:
    cdef public list ids
    cdef public list words
    cdef public list tags
    cdef public list pos
    cdef public list morphs
    cdef public list lemmas
    cdef public list heads
    cdef public list deps
    cdef public list entities
    cdef public list sent_starts
    cdef public list brackets


cdef class DocAnnotation:
    cdef public object cats
    cdef public object links


cdef class Example:
    cdef public object doc
    cdef public TokenAnnotation token_annotation
    cdef public DocAnnotation doc_annotation
    cdef public object goldparse


