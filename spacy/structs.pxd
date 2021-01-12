from libc.stdint cimport uint8_t, uint32_t, int32_t, uint64_t
from libcpp.vector cimport vector
from libcpp.unordered_set cimport unordered_set
from libcpp.unordered_map cimport unordered_map
from libc.stdint cimport int32_t, int64_t

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


cdef struct SpanC:
    hash_t id
    int start
    int end
    int start_char
    int end_char
    attr_t label
    attr_t kb_id


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


cdef struct MorphAnalysisC:
    hash_t key
    int length

    attr_t* fields
    attr_t* features


# Internal struct, for storage and disambiguation of entities.
cdef struct KBEntryC:

    # The hash of this entry's unique ID/name in the kB
    hash_t entity_hash

    # Allows retrieval of the entity vector, as an index into a vectors table of the KB.
    # Can be expanded later to refer to multiple rows (compositional model to reduce storage footprint).
    int32_t vector_index

    # Allows retrieval of a struct of non-vector features.
    # This is currently not implemented and set to -1 for the common case where there are no features.
    int32_t feats_row

    # log probability of entity, based on corpus frequency
    float freq


# Each alias struct stores a list of Entry pointers with their prior probabilities
# for this specific mention/alias.
cdef struct AliasC:

    # All entry candidates for this alias
    vector[int64_t] entry_indices

    # Prior probability P(entity|alias) - should sum up to (at most) 1.
    vector[float] probs


cdef struct EdgeC:
    hash_t label
    int32_t head
    int32_t tail


cdef struct GraphC:
    vector[vector[int32_t]] nodes
    vector[EdgeC] edges
    vector[float] weights
    vector[int] n_heads
    vector[int] n_tails
    vector[int] first_head
    vector[int] first_tail
    unordered_set[int]* roots
    unordered_map[hash_t, int]* node_map
    unordered_map[hash_t, int]* edge_map
