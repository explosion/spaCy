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
    hash_t ent_id


cdef struct MorphAnalysisC:
    univ_pos_t pos
    
    attr_t abbr
    attr_t adp_type
    attr_t adv_type
    attr_t animacy
    attr_t aspect
    attr_t case
    attr_t conj_type
    attr_t connegative
    attr_t definite
    attr_t degree
    attr_t derivation
    attr_t echo
    attr_t foreign
    attr_t gender
    attr_t hyph
    attr_t inf_form
    attr_t mood
    attr_t negative
    attr_t number
    attr_t name_type
    attr_t noun_type
    attr_t num_form
    attr_t num_type
    attr_t num_value
    attr_t part_form
    attr_t part_type
    attr_t person
    attr_t polite
    attr_t polarity
    attr_t poss
    attr_t prefix
    attr_t prep_case
    attr_t pron_type
    attr_t punct_side
    attr_t punct_type
    attr_t reflex
    attr_t style
    attr_t style_variant
    attr_t tense
    attr_t typo
    attr_t verb_form
    attr_t voice
    attr_t verb_type

