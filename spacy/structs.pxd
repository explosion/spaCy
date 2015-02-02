from libc.stdint cimport int8_t, uint8_t, uint16_t, uint32_t

from .typedefs cimport flags_t, attr_t, id_t, hash_t
from .parts_of_speech cimport univ_pos_t


cdef struct LexemeC:
    const float* repvec

    flags_t flags
   
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


cdef struct Morphology:
    uint8_t number
    uint8_t tenspect # Tense/aspect/voice
    uint8_t mood
    uint8_t gender
    uint8_t person
    uint8_t case
    uint8_t misc


cdef struct PosTag:
    Morphology morph
    int id
    univ_pos_t pos


# Start and end will be offsets: i + ent.start will always take you to the
# "next" entity start. If inside an entity, ent.start will be negative ---
# the next entity is the start of the one the token is inside.  If i _is_
# the start of an entity, then ent.start will be the beginning of the next one.
#
# The same/inverse is true for end. If ent.end has a negative value, we are either
# at the end of an entity, or outside one.  If we're inside an entity, ent.end
# will have a positive value.
#
# This allows us to easily find the span of an entity we might be inside, while
# naturally sharing an API with iterating through all entities in the sentence
cdef struct Entity:
    int32_t tag
    uint16_t flags
    int8_t start
    int8_t end


cdef struct TokenC:
    const LexemeC* lex
    Morphology morph
    Entity ent
    univ_pos_t pos
    int tag
    int idx
    int lemma
    int sense
    int head
    int dep
    bint sent_end
    uint32_t l_kids
    uint32_t r_kids


cdef struct Utf8Str:
    id_t i
    hash_t key
    unsigned char* chars
    int length


cdef struct UniStr:
    Py_UNICODE* chars
    size_t n
    hash_t key
