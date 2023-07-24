from cymem.cymem cimport Pool
from libc.stdint cimport uint32_t, uint64_t
from libcpp.pair cimport pair
from libcpp.queue cimport priority_queue
from libcpp.vector cimport vector

from ...typedefs cimport class_t, hash_t, weight_t

ctypedef pair[weight_t, size_t] Entry
ctypedef priority_queue[Entry] Queue


ctypedef int (*trans_func_t)(void* dest, void* src, class_t clas, void* x) except -1

ctypedef void* (*init_func_t)(Pool mem, int n, void* extra_args) except NULL

ctypedef int (*del_func_t)(Pool mem, void* state, void* extra_args) except -1

ctypedef int (*finish_func_t)(void* state, void* extra_args) except -1

ctypedef hash_t (*hash_func_t)(void* state, void* x) except 0


cdef struct _State:
    void* content
    class_t* hist
    weight_t score
    weight_t loss
    int i
    int t
    bint is_done


cdef class Beam:
    cdef Pool mem
    cdef class_t nr_class
    cdef class_t width
    cdef class_t size
    cdef public weight_t min_density
    cdef int t
    cdef readonly bint is_done
    cdef list histories
    cdef list _parent_histories
    cdef weight_t** scores
    cdef int** is_valid
    cdef weight_t** costs
    cdef _State* _parents
    cdef _State* _states
    cdef del_func_t del_func

    cdef int _fill(self, Queue* q, weight_t** scores, int** is_valid) except -1

    cdef inline void* at(self, int i) nogil:
        return self._states[i].content

    cdef int initialize(self, init_func_t init_func, del_func_t del_func, int n, void* extra_args) except -1
    cdef int advance(self, trans_func_t transition_func, hash_func_t hash_func,
                     void* extra_args) except -1
    cdef int check_done(self, finish_func_t finish_func, void* extra_args) except -1

    cdef inline void set_cell(self, int i, int j, weight_t score, int is_valid, weight_t cost) nogil:
        self.scores[i][j] = score
        self.is_valid[i][j] = is_valid
        self.costs[i][j] = cost

    cdef int set_row(self, int i, const weight_t* scores, const int* is_valid,
                     const weight_t* costs) except -1
    cdef int set_table(self, weight_t** scores, int** is_valid, weight_t** costs) except -1


cdef class MaxViolation:
    cdef Pool mem
    cdef weight_t cost
    cdef weight_t delta
    cdef readonly weight_t p_score
    cdef readonly weight_t g_score
    cdef readonly double Z
    cdef readonly double gZ
    cdef class_t n
    cdef readonly list p_hist
    cdef readonly list g_hist
    cdef readonly list p_probs
    cdef readonly list g_probs

    cpdef int check(self, Beam pred, Beam gold) except -1
    cpdef int check_crf(self, Beam pred, Beam gold) except -1
