from libc.stdint cimport uint8_t, uint32_t, int32_t, uint64_t

from .typedefs cimport flags_t, attr_t, hash_t
from .parts_of_speech cimport univ_pos_t


cdef struct LexemeC:
    float* vector

    flags_t flags

    attr_t lang

    attr_t id
    attr_t length

    attr_t orth
    attr_t lower
    attr_t norm
    attr_t shape
    attr_t prefix
    attr_t suffix

    attr_t cluster

    float prob
    float sentiment
    float l2_norm


cdef struct Entity:
    hash_t id
    int start
    int end
    int label


cdef struct TokenC:
    const LexemeC* lex
    uint64_t morph
    univ_pos_t pos
    bint spacy
    int tag
    int idx
    int lemma
    int sense
    int head
    int dep
    bint sent_start

    uint32_t l_kids
    uint32_t r_kids
    uint32_t l_edge
    uint32_t r_edge

    int ent_iob
    int ent_type # TODO: Is there a better way to do this? Multiple sources of truth..
    hash_t ent_id
