from libc.stdint cimport uint16_t, uint32_t, uint64_t, uintptr_t
from libc.stdint cimport uint8_t


# Reserve 64 values for flag features
cpdef enum attr_id_t:
    FLAG0
    FLAG1
    FLAG2
    FLAG3
    FLAG4
    FLAG5
    FLAG6
    FLAG7
    FLAG8
    FLAG9
    FLAG10
    FLAG11
    FLAG12
    FLAG13
    FLAG14
    FLAG15
    FLAG16
    FLAG17
    FLAG18
    FLAG19
    FLAG20
    FLAG21
    FLAG22
    FLAG23
    FLAG24
    FLAG25
    FLAG26
    FLAG27
    FLAG28
    FLAG29
    FLAG30
    FLAG31
    FLAG32
    FLAG33
    FLAG34
    FLAG35
    FLAG36
    FLAG37
    FLAG38
    FLAG39
    FLAG40
    FLAG41
    FLAG42
    FLAG43
    FLAG44
    FLAG45
    FLAG46
    FLAG47
    FLAG48
    FLAG49
    FLAG50
    FLAG51
    FLAG52
    FLAG53
    FLAG54
    FLAG55
    FLAG56
    FLAG57
    FLAG58
    FLAG59
    FLAG60
    FLAG61
    FLAG62
    FLAG63

    ID
    ORTH
    LOWER
    NORM
    SHAPE
    PREFIX
    SUFFIX

    LENGTH
    CLUSTER
    LEMMA
    POS
    TAG
    DEP
    ENT



ctypedef uint64_t hash_t
ctypedef char* utf8_t
ctypedef uint32_t attr_t
ctypedef uint64_t flags_t
ctypedef uint32_t id_t
ctypedef uint16_t len_t
ctypedef uint16_t tag_t
