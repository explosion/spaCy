from libcpp.vector cimport vector
from libcpp.pair cimport pair

from preshed.counter cimport count_t
from preshed.maps cimport PreshMap
from preshed.counter cimport PreshCounter
from cymem.cymem cimport Pool

from .lang cimport Lexicon
from .tokens cimport Tokens, TokenC
from .typedefs cimport id_t
from .lexeme cimport attr_id_t
from .typedefs cimport attr_t
from .typedefs cimport hash_t

from murmurhash.mrmr cimport hash64


ctypedef vector[pair[id_t, count_t]] count_vector_t


cdef class Index:
    cdef attr_id_t attr_id
    cdef readonly attr_t max_value
    cdef vector[count_vector_t] counts
    
    cpdef int count(self, Tokens tokens) except -1


cdef class DecisionMemory:
    cdef int n_classes
    cdef Pool mem
    cdef PreshCounter _counts
    cdef PreshCounter _class_counts
    cdef PreshMap memos
    cdef list class_names
    
    cdef int inc(self, hash_t context_key, hash_t clas, count_t inc) except -1
    cdef int find_best_class(self, count_t* counts, hash_t context_key) except -1

    cdef inline int get(self, hash_t context_key) nogil:
        return <int><size_t>self.memos.get(context_key) - 1


