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
from preshed.maps cimport PreshMap
from murmurhash.mrmr cimport hash64
from .strings cimport StringStore, hash_string

from cymem.cymem cimport Pool
cimport numpy as np
import numpy as np
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
    def __init__(self):
        self.data = VectorStore()
        self.strings = StringStore()

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
            (norm, vector): tuple[float32, float32[:self.nr_dim]]
        '''
        idx = self.strings[key]
        if idx == self.data.vectors.size():
            self.add_empty(key, self.nr_dim)
        return self.data[idx]

    def __setitem__(self, unicode key, float[:] value):
        '''Assign a (frequency, vector) tuple to the vector map.

        Arguments:
            key unicode
            value float32[:self.nr_dim]
        Returns:
            None
        '''
        idx = self.strings[key]
        if self.data.vectors.size() == idx:
            self.data.add(value)
        else:
            self.data.set(idx, value)

    def __iter__(self):
        '''Iterate over the keys in the map, in order of insertion.

        Generates:
            key unicode
        '''
        yield from self.strings

    def add(self, unicode string, float[:] vector):
        '''Insert a vector into the map by value. Makes a copy of the vector.
        '''
        if string not in self.strings:
            idx = self.strings[string]
            if self.data.vectors.size() != idx:
                raise IOError("oops") 
            self.data.add(vector)
        else:
            idx = self.strings[string]
            self.data.set(idx, vector)
        return idx

    def add_empty(self, unicode string, int size):
        '''Insert a vector into the map by value. Makes a copy of the vector.
        '''
        idx = self.strings[string]
        if self.data.vectors.size() != idx:
            raise IOError("oops") 
        self.data.add_empty(size)
        return idx

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

    def resize(self, new_size):
        self.data.resize(new_size)

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

    def norm(self, i):
        return self.data.norm(i)

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
    def __init__(self):
        self.mem = Pool()
        self.nr_dim = -1 # => unset 
	#allocate large - not knowing actual size yet
        zeros = <float *>self.mem.alloc(1000, sizeof(float))
        self.vectors.push_back(zeros)
        self.norms.push_back(0)

#    cdef void add(self, float * vector):
#        self.vectors.push_back(vector);
#        self.norm.pushback(np.linalg.norm(np.asarray(<float[:self.nr_dim]>vector)))

    def add(self, float [:] vector):
        if self.nr_dim == -1:
            self.nr_dim = len(vector)
        else:
            assert self.nr_dim == len(vector)
        v = np.asarray(vector)
        norm = 0
        if len([value for i, value in enumerate(v) if value != 0]) != 0:
            norm = np.linalg.norm(vector)
            v /= norm
        cdef float *newvec  = <float *>self.mem.alloc(self.nr_dim, sizeof(float))
        for i in xrange(self.nr_dim):
            newvec[i] = v[i]
        self.vectors.push_back(newvec);
        self.norms.push_back(norm)

    def add_empty(self, int size):
        if self.nr_dim == -1:
            self.nr_dim = size
        else:
            assert self.nr_dim == size
        cdef float *newvec  = <float *>self.mem.alloc(self.nr_dim, sizeof(float))
        for i in xrange(self.nr_dim):
            newvec[i] = 0.0
        self.vectors.push_back(newvec);
        self.norms.push_back(0)

    def norm(self, i):
        return self.norms[i]

    def resize(self, new_size):
        if self.nr_dim == new_size:
            return
        for i in range(1, self.vectors.size()):
            self.vectors[i] = <float*>self.mem.realloc(self.vectors[i],
                                        new_size * sizeof(float))
        self.nr_dim = new_size    

    def __getitem__(self, int i):
        cdef float* ptr = self.vectors.at(i)
        cv = <float[:self.nr_dim]>ptr
        return (self.norms[i], np.asarray(cv))

    def set(self, int i, float[:] vector):
        cdef float* ptr = self.vectors.at(i)
        v = np.asarray(vector)
        norm = 0
        if len([value for i, value in enumerate(v) if value != 0]) != 0:
            norm = np.linalg.norm(vector)
            v /= norm
        self.norms[i] = norm
        for j, value in enumerate(v):
            ptr[j] = value

    # def save(self, loc):
    #     cdef int fd
    #     cdef uint32_t map_size, row, off
    #     cdef float *norms, *vec
    #     cdef int32_t vec_count = self.vectors.size()
    #     cdef int32_t nr_dim = self.nr_dim
    #     map_size = vec_count*nr_dim*sizeof(float) + sizeof(*vh)
    #     truncate(loc, map_size)
    #     fd = posix.fcntl.open(loc, posix.fcntl.O_RDWR)
    #     vh = <_VectorHeader*>mmap(NULL, map_size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0)
    #     norms = &(<float*>vh)[1]
    #     vec = &norms[vec_count]
    #     init_vh(vh, vec_count, nr_dim)
    #     off =row = 0
    #     for v in self.vectors:
    #         off = row*nr_dim
    #         norms[row] = get_let_norm(v, nr_dim)
    #         for i in nr_dim:
    #             vec[off + i] = v[i]
    #     close(fd)
    #     munmap(<void *>vh, map_size)

    def load(self, loc, strings):
        cdef int fd
        cdef uint32_t nr_dim, vec_count
        cdef float *norms
        cdef float *vec
        cdef vector_header *vh
        cdef vector_section *vs
        vh = vec_load_setup(loc)
        print "loading from ", loc
        # assume mat / norms / strings for
        # first cut
        # first fetch mats
        vs = <vector_section*>&vh[1]
        vec = <float *>(<uint64_t>vh + vs.vs_off)
        vec_count = vs.vs_dims[0]
        nr_dim = vs.vs_dims[1]
        if self.nr_dim == -1:
            self.nr_dim = nr_dim
        elif self.nr_dim != nr_dim:
            raise IOError("dimension mismatch in input")
        # then norms
        vs = <vector_section*>&vs[1]
        norms = <float *>(<uint64_t>vh + vs.vs_off)
        # then strings
        vs = <vector_section*>&vs[1]
        strptr = <char *>(<uint64_t>vh + vs.vs_off)
        cdef bytes py_string
        for i in range(vec_count):
            # we can't pass the float pointer to python
            # and then recover the float * again, so
            # we just store directly here without add()
            self.norms.push_back(norms[i])
            self.vectors.push_back(&vec[nr_dim*i])
            len = strlen(strptr)
            py_string = strptr
            strings[py_string]
            strptr += len + 1
