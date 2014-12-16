"""Create a term-document matrix"""
cimport cython

from libc.string cimport memmove

from cymem.cymem cimport Address

from .lexeme cimport Lexeme, get_attr
from .tokens cimport TokenC
from .typedefs cimport hash_t

from preshed.maps cimport MapStruct, Cell, map_get, map_set, map_init


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



cdef class PosMemory:
    def __init__(self, tag_names):
        self.tag_names = tag_names
        self.nr_tags = len(tag_names)
        self.mem = Pool()
        self._counts = PreshCounter()
        self._pos_counts = PreshCounter()

    def __getitem__(self, ids):
        cdef id_t[2] ngram
        ngram[0] = ids[0]
        ngram[1] = ids[1]
        cdef hash_t ngram_key = hash64(ngram, 2 * sizeof(id_t), 0)
        cdef hash_t[2] pos_context
        pos_context[0] = ngram_key
        counts = {}
        cdef id_t i
        for i, tag in enumerate(self.tag_names):
            pos_context[1] = <hash_t>i
            key = hash64(pos_context, sizeof(hash_t) * 2, 0)
            count = self._pos_counts[key]
            counts[tag] = count
        return counts

    @cython.cdivision(True)
    def iter_ngrams(self, float min_acc=0.99, count_t min_freq=10):
        cdef Address counts_addr = Address(self.nr_tags, sizeof(count_t))
        cdef count_t* counts = <count_t*>counts_addr.ptr
        cdef MapStruct* ngram_counts = self._counts.c_map
        cdef hash_t ngram_key
        cdef count_t ngram_freq
        cdef int best_pos
        cdef float acc

        cdef int i
        for i in range(ngram_counts.length):
            ngram_key = ngram_counts.cells[i].key
            ngram_freq = <count_t>ngram_counts.cells[i].value
            if ngram_key != 0 and ngram_freq >= min_freq:
                best_pos = self.find_best_pos(counts, ngram_key)
                acc = counts[best_pos] / ngram_freq
                if acc >= min_acc:
                    yield counts[best_pos], ngram_key, best_pos
        
    cpdef int count(self, Tokens tokens) except -1:
        cdef int i
        cdef TokenC* t
        for i in range(tokens.length):
            t = &tokens.data[i]
            if t.lex.prob != 0 and t.lex.prob >= -14:
                self.inc(t, 1)

    cdef int inc(self, TokenC* word, count_t inc) except -1:
        cdef hash_t[2] ngram_pos_context
        cdef hash_t ngram_key = self._ngram_key(word)
        ngram_pos_context[0] = ngram_key
        ngram_pos_context[1] = <hash_t>word.pos
        ngram_pos_key = hash64(ngram_pos_context, 2 * sizeof(hash_t), 0)
        self._counts.inc(ngram_key, inc)
        self._pos_counts.inc(ngram_pos_key, inc)

    cdef int find_best_pos(self, count_t* counts, hash_t ngram_key) except -1:
        cdef hash_t[2] unhashed_key
        unhashed_key[0] = ngram_key
        
        cdef count_t total = 0
        cdef hash_t key
        cdef int pos
        cdef int best
        cdef int mode = 0
        for pos in range(self.nr_tags):
            unhashed_key[1] = <hash_t>pos
            key = hash64(unhashed_key, sizeof(hash_t) * 2, 0)
            count = self._pos_counts[key]
            counts[pos] = count
            if count >= mode:
                mode = count
                best = pos
            total += count
        return best

    cdef count_t ngram_count(self, TokenC* word) except -1:
        cdef hash_t ngram_key = self._ngram_key(word)
        return self._counts[ngram_key]

    cdef hash_t _ngram_key(self, TokenC* word) except 0:
        cdef id_t[2] context
        context[0] = word.lex.sic
        context[1] = word[-1].lex.sic
        return hash64(context, sizeof(id_t) * 2, 0)
