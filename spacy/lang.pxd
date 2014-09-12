from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t
from spacy.word cimport Lexeme
from spacy.tokens cimport Tokens
from spacy.lexeme cimport LexemeC

from libcpp.utility cimport pair
from libcpp.vector cimport vector
from libc.stdint cimport uint64_t, int64_t


cdef extern from "Python.h":
    cdef bint Py_UNICODE_ISSPACE(Py_UNICODE ch)
    cdef bint Py_UNICODE_ISALNUM(Py_UNICODE ch)


cdef extern from "sparsehash/dense_hash_map" namespace "google":
    cdef cppclass dense_hash_map[K, D]:
        K& key_type
        D& data_type
        pair[K, D]& value_type
        uint64_t size_type
        cppclass iterator:
            pair[K, D]& operator*() nogil
            iterator operator++() nogil
            iterator operator--() nogil
            bint operator==(iterator) nogil
            bint operator!=(iterator) nogil
        iterator begin()
        iterator end()
        uint64_t size()
        uint64_t max_size()
        bint empty()
        uint64_t bucket_count()
        uint64_t bucket_size(uint64_t i)
        uint64_t bucket(K& key)
        double max_load_factor()
        void max_load_vactor(double new_grow)
        double min_load_factor()
        double min_load_factor(double new_grow)
        void set_resizing_parameters(double shrink, double grow)
        void resize(uint64_t n)
        void rehash(uint64_t n)
        dense_hash_map()
        dense_hash_map(uint64_t n)
        void swap(dense_hash_map&)
        pair[iterator, bint] insert(pair[K, D]) nogil
        void set_empty_key(K&)
        void set_deleted_key(K& key)
        void clear_deleted_key()
        void erase(iterator pos)
        uint64_t erase(K& k)
        void erase(iterator first, iterator last)
        void clear()
        void clear_no_resize()
        pair[iterator, iterator] equal_range(K& k)
        D& operator[](K&) nogil


cdef class Lexicon:
    cpdef readonly size_t size

    cpdef Lexeme lookup(self, unicode string)
    cdef size_t get(self, Py_UNICODE* characters, size_t length)
    
    cdef dense_hash_map[uint64_t, size_t] _dict
    
    cdef list _string_features
    cdef list _flag_features


cdef class Language:
    cdef unicode name
    cdef dict cache
    cdef dict specials
    cpdef readonly Lexicon lexicon
    cpdef readonly object tokens_class

    cpdef Tokens tokenize(self, unicode text)
    cpdef Lexeme lookup(self, unicode text)

    cdef _tokenize(self, Tokens tokens, Py_UNICODE* characters, size_t length)
    cdef int _split_one(self, Py_UNICODE* characters, size_t length)
