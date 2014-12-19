"""Create a term-document matrix"""
cimport cython
from libc.stdint cimport int64_t
from libc.string cimport memmove

from cymem.cymem cimport Address

from .lexeme cimport Lexeme, get_attr
from .tokens cimport TokenC
from .typedefs cimport hash_t

from preshed.maps cimport MapStruct, Cell, map_get, map_set, map_init
from murmurhash.mrmr cimport hash64


cdef class Index:
    def __init__(self, attr_id_t attr_id):
        self.attr_id = attr_id
        self.max_value = 0

    cpdef int count(self, Tokens tokens) except -1:
        cdef PreshCounter counts = PreshCounter(2 ** 8)
        cdef attr_id_t attr_id = self.attr_id
        cdef attr_t term
        cdef int i
        for i in range(tokens.length):
            term = get_attr(tokens.data[i].lex, attr_id)
            counts.inc(term, 1)
            if term > self.max_value:
                self.max_value = term
        cdef count_t count
        cdef count_vector_t doc_counts
        for term, count in counts:
            doc_counts.push_back(pair[id_t, count_t](term, count))
        self.counts.push_back(doc_counts)


cdef class DecisionMemory:
    def __init__(self, class_names):
        self.class_names = class_names
        self.n_classes = len(class_names)
        self.mem = Pool()
        self._counts = PreshCounter()
        self._class_counts = PreshCounter()
        self.memos = PreshMap()

    def load(self, loc, thresh=50):
        cdef:
            count_t freq
            hash_t key
            int clas
        for line in open(loc):
            freq, key, clas = [int(p) for p in line.split()]
            if thresh == 0 or freq >= thresh:
                self.memos.set(key, <void*>(clas+1))

    def __getitem__(self, ids):
        cdef id_t[2] context
        context[0] = context[0]
        context[1] = context[1]
        cdef hash_t context_key = hash64(context, 2 * sizeof(id_t), 0)
        cdef hash_t[2] class_context
        class_context[0] = context_key
        counts = {}
        cdef id_t i
        for i, clas in enumerate(self.clas_names):
            class_context[1] = <hash_t>i
            key = hash64(class_context, sizeof(hash_t) * 2, 0)
            count = self._class_counts[key]
            counts[clas] = count
        return counts

    @cython.cdivision(True)
    def iter_contexts(self, float min_acc=0.99, count_t min_freq=10):
        cdef Address counts_addr = Address(self.n_classes, sizeof(count_t))
        cdef count_t* counts = <count_t*>counts_addr.ptr
        cdef MapStruct* context_counts = self._counts.c_map
        cdef hash_t context_key
        cdef count_t context_freq
        cdef int best_class
        cdef float acc

        cdef int i
        for i in range(context_counts.length):
            context_key = context_counts.cells[i].key
            context_freq = <count_t>context_counts.cells[i].value
            if context_key != 0 and context_freq >= min_freq:
                best_class = self.find_best_class(counts, context_key)
                acc = counts[best_class] / context_freq
                if acc >= min_acc:
                    yield counts[best_class], context_key, best_class
        
    cdef int inc(self, hash_t context_key, hash_t clas, count_t inc) except -1:
        cdef hash_t context_and_class_key
        cdef hash_t[2] context_and_class
        context_and_class[0] = context_key
        context_and_class[1] = clas
        context_and_class_key = hash64(context_and_class, 2 * sizeof(hash_t), 0)
        self._counts.inc(context_key, inc)
        self._class_counts.inc(context_and_class_key, inc)

    cdef int find_best_class(self, count_t* counts, hash_t context_key) except -1:
        cdef hash_t[2] unhashed_key
        unhashed_key[0] = context_key
        
        cdef count_t total = 0
        cdef hash_t key
        cdef int clas
        cdef int best
        cdef int mode = 0
        for clas in range(self.n_classes):
            unhashed_key[1] = <hash_t>clas
            key = hash64(unhashed_key, sizeof(hash_t) * 2, 0)
            count = self._class_counts[key]
            counts[clas] = count
            if count >= mode:
                mode = count
                best = clas
            total += count
        return best
