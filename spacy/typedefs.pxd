from libc.stdint cimport uint16_t, uint32_t, uint64_t, uintptr_t
from libc.stdint cimport uint8_t

ctypedef uint64_t hash_t
ctypedef char* utf8_t
ctypedef uint32_t attr_t
ctypedef uint64_t flags_t
ctypedef uint32_t id_t
ctypedef uint16_t len_t
ctypedef uint16_t tag_t


cdef struct Morphology:
    uint8_t number
    uint8_t tenspect # Tense/aspect/voice
    uint8_t mood
    uint8_t gender
    uint8_t person
    uint8_t case
    uint8_t misc
