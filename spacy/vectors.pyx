# cython: profile=True
# cython: cdivision=True
# cython: infer_types=True
cimport cython.parallel
cimport cpython.array

from libc.stdint cimport uint8_t, uint16_t 
from libc.stdint cimport uint32_t, int32_t
from libc.stdint cimport uint64_t
from libc.string cimport memcpy
from libc.math cimport sqrt

from libcpp.pair cimport pair
from libcpp.queue cimport priority_queue
from libcpp.vector cimport vector
from spacy.cfile cimport CFile
from preshed.maps cimport PreshMap
from spacy.strings cimport StringStore, hash_string
from murmurhash.mrmr cimport hash64

from cymem.cymem cimport Pool
cimport numpy as np
import numpy
from os import path
try:
    import ujson as json
except ImportError:
    import json

cimport posix.fcntl
from posix.unistd cimport close, read, off_t
cdef extern from "string.h":
    size_t strlen(const char *s)

ctypedef pair[float, int] Entry
ctypedef priority_queue[Entry] Queue

from txtvec2bin cimport vector_section, vector_header, vec_load_setup

cdef class VectorMap:
    '''Provide key-based access into the VectorStore. Keys are unicode strings.'''
    def __init__(self, nr_dim):
        self.data = VectorStore(nr_dim)
        self.strings = StringStore()
#        self.freqs = PreshMap()

    @property
    def nr_dim(self):
        return self.data.nr_dim

    def __len__(self):
        '''Number of entries in the map.

        Returns: length int >= 0
        '''
        return self.data.vectors.size()

    def __contains__(self, unicode string):
        '''Check whether the VectorMap has a given key.

        Returns: has_key bool
        '''
        cdef uint64_t hashed = hash_string(string)
        return bool(self.strings[hashed])

    def __getitem__(self, unicode key):
        '''Retrieve a vector tuple from the vector map, or
        raise KeyError if the key is not found.

        Arguments:
            key unicode

        Returns:
            float32[:self.nr_dim]
        '''
        i = self.strings[key]
        return self.data[i]

    def __setitem__(self, unicode key, value):
        '''Assign a (frequency, vector) tuple to the vector map.

        Arguments:
            key unicode
            value float32[:self.nr_dim]
        Returns:
            None
        '''
        # TODO: Handle case where we're over-writing an existing entry.
        cdef float[:] vector
        vector = value
        idx = self.strings[key]
        assert self.data.vectors.size() == idx
        self.data.add(vector)

    def __iter__(self):
        '''Iterate over the keys in the map, in order of insertion.

        Generates:
            key unicode
        '''
        yield from self.strings

    def keys(self):
        '''Iterate over the keys in the map, in order of insertion.

        Generates:
            key unicode
        '''
        yield from self.strings

    def values(self):
        '''Iterate over the values in the map, in order of insertion.

        Generates:
            vector float32[:self.nr_dim]
        '''
        for key, value in self.items():
            yield value

    def items(self):
        '''Iterate over the items in the map, in order of insertion.

        Generates:
            (key, vector): tuple[string, float32[:self.nr_dim]]
        '''
        for i, string in enumerate(self.strings):
            yield string, self.data[i]

    def add(self, unicode string, int freq, float[:] vector):
        '''Insert a vector into the map by value. Makes a copy of the vector.
        '''
        idx = self.strings[string]
        assert self.data.vectors.size() == idx
        self.data.add(vector)

    # def save(self, data_dir):
    #     '''Serialize to a directory.

    #     * data_dir/strings.json --- The keys, in insertion order.
    #     * data_dir/freqs.json --- The frequencies.
    #     * data_dir/vectors.bin --- The vectors.
    #     '''
    #     with open(path.join(data_dir, 'strings.json'), 'w') as file_:
    #         self.strings.dump(file_)
    #     self.data.save(path.join(data_dir, 'vectors.bin'))
    #     freqs = []
    #     cdef uint64_t hashed
    #     for string in self.strings:
    #         hashed = hash_string(string)
    #         freq = self.freqs[hashed]
    #         if not freq:
    #             continue
    #         freqs.append([string, freq])
    #     with open(path.join(data_dir, 'freqs.json'), 'w') as file_:
    #         json.dump(freqs, file_)

    def load(self, loc):
        '''Load from a binary file:
        * loc --- The binary with the vectors and strings.
        '''
        self.data.load(loc, self.strings)

cdef class VectorStore:
    '''Maintain an array of float* pointers for word vectors, which the
    table may or may not own. Keys and frequencies sold separately --- 
    we're just a dumb vector of data, that knows how to run linear-scan
    similarity queries.'''
    def __init__(self, int nr_dim):
        self.mem = Pool()
        self.nr_dim = nr_dim
        zeros = <float *>self.mem.alloc(self.nr_dim, sizeof(float))
        self.vectors.push_back(zeros)
        self.norms.push_back(0)
        self.cache = PreshMap(100000)

    def __getitem__(self, int i):
        cdef float* ptr = self.vectors.at(i)
        cv = <float[:self.nr_dim]>ptr
        return numpy.asarray(cv)

    def add(self, float[:] vec, float norm):
        assert len(vec) == self.nr_dim
        self.norms.push_back(norm)
        self.vectors.push_back(<float *>vec)

    # def save(self, loc):
    #     cdef int fd
    #     cdef uint32_t map_size, row, off
    #     cdef float *norms, *vec
    #     cdef int32_t vec_count = self.vectors.size()
    #     cdef int32_t nr_dims = self.nr_dim
    #     map_size = vec_count*nr_dims*sizeof(float) + sizeof(*vh)
    #     truncate(loc, map_size)
    #     fd = posix.fcntl.open(loc, posix.fcntl.O_RDWR)
    #     vh = <_VectorHeader*>mmap(NULL, map_size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0)
    #     norms = &(<float*>vh)[1]
    #     vec = &norms[vec_count]
    #     init_vh(vh, vec_count, nr_dims)
    #     off =row = 0
    #     for v in self.vectors:
    #         off = row*nr_dims
    #         norms[row] = get_let_norm(v, nr_dims)
    #         for i in nr_dims:
    #             vec[off + i] = v[i]
    #     close(fd)
    #     munmap(<void *>vh, map_size)

    def load(self, loc, strings):
        cdef int fd
        cdef uint32_t nr_dims, vec_count
        cdef float *norms
        cdef float *vec
        cdef vector_header *vh
        cdef vector_section *vs
        vh = vec_load_setup(loc)
        # assume mat / norms / strings for
        # first cut
        # first fetch mats
        vs = <vector_section*>&vh[1]
        vec = <float *>(<uint64_t>vh + vs.vs_off)
        vec_count = vs.vs_dims[0]
        nr_dims = vs.vs_dims[1]
        # then norms
        vs = <vector_section*>&vs[1]
        norms = <float *>(<uint64_t>vh + vs.vs_off)
        # then strings
        vs = <vector_section*>&vs[1]
        strings = <char *>(<uint64_t>vh + vs.vs_off)
        cdef float[:] cv
        cdef bytes py_string
        for i in range(vec_count):
            cv = <float[:nr_dims]>&vec[nr_dims*i]
            self.add(cv, norms[i])
            py_string = strings
            strings.intern_unicode(py_string)
            strings += strlen(strings) + 1
