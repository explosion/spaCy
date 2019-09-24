from preshed.maps cimport key_t

cdef struct MatchStruct:
    key_t match_id
    int start
    int end
