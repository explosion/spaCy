from libc.stdint cimport uint8_t, uint32_t, int32_t, uint64_t

from .typedefs cimport flags_t, attr_t, hash_t
from .parts_of_speech cimport univ_pos_t


cdef struct LexemeC:
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


cdef struct SerializedLexemeC:
    unsigned char[8 + 8*10 + 4 + 4] data
    #    sizeof(flags_t)  # flags
    #    + sizeof(attr_t) # lang
    #    + sizeof(attr_t) # id
    #    + sizeof(attr_t) # length
    #    + sizeof(attr_t) # orth
    #    + sizeof(attr_t) # lower
    #    + sizeof(attr_t) # norm
    #    + sizeof(attr_t) # shape
    #    + sizeof(attr_t) # prefix
    #    + sizeof(attr_t) # suffix
    #    + sizeof(attr_t) # cluster
    #    + sizeof(float)  # prob
    #    + sizeof(float)  # cluster
    #    + sizeof(float) # l2_norm


cdef struct Entity:
    hash_t id
    int start
    int end
    attr_t label


cdef struct TokenC:
    const LexemeC* lex
    uint64_t morph
    univ_pos_t pos
    bint spacy
    attr_t tag
    int idx
    attr_t lemma
    attr_t norm
    int head
    attr_t dep

    uint32_t l_kids
    uint32_t r_kids
    uint32_t l_edge
    uint32_t r_edge

    int sent_start
    int ent_iob
    attr_t ent_type # TODO: Is there a better way to do this? Multiple sources of truth..
    attr_t ent_kb_id
    hash_t ent_id
