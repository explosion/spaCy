from libcpp.vector cimport vector

from cymem.cymem cimport Pool
from preshed.maps cimport key_t, MapStruct

from ..attrs cimport attr_id_t
from ..tokens.doc cimport Doc
from ..vocab cimport Vocab


cdef class PhraseMatcher:
    cdef Vocab vocab
    cdef attr_id_t attr
    cdef object _callbacks
    cdef object _docs
    cdef bint _validate
    cdef MapStruct* c_map
    cdef Pool mem
    cdef key_t _terminal_hash

    cdef void find_matches(self, Doc doc, vector[MatchStruct] *matches) nogil


cdef struct MatchStruct:
    key_t match_id
    int start
    int end
