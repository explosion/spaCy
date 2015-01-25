from libc.stdint cimport uint8_t, uint32_t

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


cdef struct TokenC:
    const LexemeC* lex
    Morphology morph
    univ_pos_t pos
    int tag
    int idx
    int lemma
    int sense
    int head
    int dep
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
