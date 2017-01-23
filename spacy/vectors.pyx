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
cdef extern from "sys/mman.h":
    void *mmap(void *addr, size_t len, int prot, int flags, int fd, off_t offset)
    int munmap(void *addr, size_t length)
    enum:
        PROT_READ
        PROT_WRITE
        MAP_SHARED
        MAP_PRIVATE

cdef extern from "string.h":
    size_t strlen(const char *s)

cdef extern from "sys/stat.h":
    cdef struct stat:
        off_t st_size
    int fstat(int fildes, stat *buf)

ctypedef pair[float, int] Entry
ctypedef priority_queue[Entry] Queue
ctypedef float (*do_similarity_t)(const float* v1, const float* v2,
        int nr_dim) nogil

cdef extern from "glove2bin.h":
    cdef struct vector_header:
        uint64_t vh_magic
        uint16_t vh_version
        uint16_t vh_type
        uint16_t vh_nsections
    cdef struct vector_section:
        uint64_t vs_off
        uint64_t vs_len
        uint8_t  vs_type
        uint8_t  vs_precision
        uint32_t vs_dims[3]
    enum:
        VH_TYPE_GLOVE
        VH_TYPE_CLUSTER
        VH_TYPE_DOC
        VS_FLOAT8
        VS_FLOAT16
        VS_FLOAT32
        VS_FLOAT64
        VS_VECTOR
        VS_MATRIX
        VS_STRING

cdef struct _CachedResult:
    int* indices
    float* scores
    int n

cdef void init_vh(vector_header *v):
    v.vh_magic =  0xF00EBEEFCAFEBABE
    v.vh_version = 1
    v.vh_type = VH_TYPE_DOC
    v.vh_nsections = 2

cdef void init_vs_mat(vector_section *v, uint64_t off, uint64_t len, uint32_t m, uint32_t n):
    v.vs_off = off
    v.vs_len = len
    v.vs_type = VS_MATRIX
    v.vs_dims[0] = m
    v.vs_dims[1] = n
 
cdef void init_vs_vec(vector_section *v, uint64_t off, uint64_t len, uint32_t m):
    v.vs_off = off
    v.vs_len = len
    v.vs_type = VS_VECTOR
    v.vs_dims[0] = m

cdef void init_vs_str(vector_section *v, uint64_t off, uint64_t len):
    v.vs_type = VS_STRING
    v.vs_off = off
    v.vs_len = len
    


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

    # def __contains__(self, unicode string):
    #     '''Check whether the VectorMap has a given key.

    #     Returns: has_key bool
    #     '''
    #     cdef uint64_t hashed = hash_string(string)
    #     return bool(self.strings[hashed])

    def __getitem__(self, unicode key):
        '''Retrieve a vector tuple from the vector map, or
        raise KeyError if the key is not found.

        Arguments:
            key unicode

        Returns:
            tuple[int, float32[:self.nr_dim]]
        '''
        i = self.strings[key]
        return self.data[i]

    def __setitem__(self, unicode key, value):
        '''Assign a (frequency, vector) tuple to the vector map.

        Arguments:
            key unicode
            value tuple[int, float32[:self.nr_dim]]
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
            (key, (freq,vector)): tuple[int, float32[:self.nr_dim]]
        '''
        for i, string in enumerate(self.strings):
            yield string, self.data[i]

    def most_similar(self, float[:] vector, int n=10):
        '''Find the keys of the N most similar entries, given a vector.

        Arguments:
            vector float[:]
            n int default=10

        Returns:
            list[unicode] length<=n
        '''
        indices, scores = self.data.most_similar(vector, n)
        return [self.strings[idx] for idx in indices], scores

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

    def similarity(self, float[:] v1, float[:] v2):
        '''Measure the similarity between two vectors, using cosine.
        
        Arguments:
            v1 float[:]
            v2 float[:]

        Returns:
            similarity_score -1<float<=1
        '''
        return cosine_similarity(&v1[0], &v2[0], len(v1))

    def most_similar(self, float[:] query, int n):
        cdef int[:] indices = np.ndarray(shape=(n,), dtype='int32')
        cdef float[:] scores = np.ndarray(shape=(n,), dtype='float32')
        cdef uint64_t cache_key = hash64(&query[0], sizeof(query[0]) * n, 0)
        cached_result = <_CachedResult*>self.cache.get(cache_key)
        if cached_result is not NULL and cached_result.n == n:
            memcpy(&indices[0], cached_result.indices, sizeof(indices[0]) * n)
            memcpy(&scores[0], cached_result.scores, sizeof(scores[0]) * n)
        else:
            # This shouldn't happen. But handle it if it does
            if cached_result is not NULL:
                if cached_result.indices is not NULL:
                    self.mem.free(cached_result.indices)
                if cached_result.scores is not NULL:
                    self.mem.free(cached_result.scores)
                self.mem.free(cached_result)
            self._similarities.resize(self.vectors.size())
            linear_similarity(&indices[0], &scores[0], &self._similarities[0],
                n, &query[0], self.nr_dim,
                &self.vectors[0], self.vectors.size(), 
                cosine_similarity)
            cached_result = <_CachedResult*>self.mem.alloc(sizeof(_CachedResult), 1)
            cached_result.n = n
            cached_result.indices = <int*>self.mem.alloc(
                sizeof(cached_result.indices[0]), n)
            cached_result.scores = <float*>self.mem.alloc(
                sizeof(cached_result.scores[0]), n)
            self.cache.set(cache_key, cached_result)
            memcpy(cached_result.indices, &indices[0], sizeof(indices[0]) * n)
            memcpy(cached_result.scores, &scores[0], sizeof(scores[0]) * n)
        return indices, scores

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
        cdef stat sb
        fd = posix.fcntl.open(loc, posix.fcntl.O_RDONLY)
        fstat(fd, &sb)
        vh = <vector_header*>mmap(NULL, sb.st_size, PROT_READ, MAP_SHARED, fd, 0)
        close(fd) # mmap maintains a reference
        # assume mat / norms / strings for now 
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


cdef void linear_similarity(int* indices, float* scores, float* tmp,
        int nr_out, const float* query, int nr_dim,
        const float* const* vectors, int nr_vector,
        do_similarity_t get_similarity) nogil:
    # Initialize the partially sorted heap
    cdef int i
    cdef float score
    for i in cython.parallel.prange(nr_vector, nogil=True):
        tmp[i] = get_similarity(query, vectors[i], nr_dim)
    cdef priority_queue[pair[float, int]] queue
    cdef float cutoff = 0
    for i in range(nr_vector):
        score = tmp[i]
        if score > cutoff:
            queue.push(pair[float, int](-score, i))
            cutoff = -queue.top().first
            if queue.size() > nr_out:
                queue.pop()
    # Fill the outputs
    i = 0
    while i < nr_out and not queue.empty(): 
        entry = queue.top()
        scores[nr_out-(i+1)] = -entry.first
        indices[nr_out-(i+1)] = entry.second
        queue.pop()
        i += 1

cdef float dotp(const float *v1, const float *v2, int n) nogil:
    dot = dot0 = dot1 = dot2 = dot3 = tmp0 = tmp1 = 0.0
    # note that there is guaranteed to be a vectorized
    # dot product implementation that we should really
    # be using to give us 4-8x speed up here - but at
    # the very least we can let the compiler try by 
    # doing 4 at a time
    for idx in range(n/4):
        i = idx*4
        dot0 = v1[i] * v2[i]
        dot1 = v1[i+1] * v2[i+1]
        dot2 = v1[i+2] * v2[i+2]
        dot3 = v1[i+3] * v2[i+3]
        tmp0 = dot0 + dot1
        tmp1 = dot2 + dot3
        dot += tmp0 + tmp1

    rem = (n%4) + 1
    for j in range(rem):
        dot += v1[i+j] * v2[i+j]
    return dot
        
cdef float get_l2_norm(const float* vec, int n) nogil:
    cdef double norm = 0.0
    norm = dotp(vec, vec, n)
    return sqrt(norm)


cdef float cosine_similarity(const float* v1, const float* v2,
        int n) nogil:
    return dotp(v1, v2, n)
