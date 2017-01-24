import numpy as np

from posix.unistd cimport close, read, off_t
cimport posix.fcntl
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
    char *strcpy(char *dest, const char *src);
           
cdef void init_vh(vector_header *v):
    v.vh_magic =  VH_MAGIC
    v.vh_version = VH_GLOVE_VERSION
    v.vh_type = VH_TYPE_DOC
    v.vh_nsections = 2

cdef void init_vs_mat(vector_section *v, char *name, uint64_t off, uint64_t len, uint32_t m, uint8_t precision, uint32_t n):
    v.vs_off = off
    v.vs_len = len
    v.vs_type = VS_MATRIX
    v.vs_precision = precision
    v.vs_dims[0] = m
    v.vs_dims[1] = n
 
cdef void init_vs_vec(vector_section *v, char *name, uint64_t off, uint64_t len, uint8_t precision, uint32_t m):
    v.vs_off = off
    v.vs_len = len
    v.vs_type = VS_VECTOR
    v.vs_dims[0] = m

cdef void init_vs_str(vector_section *v, char *name, uint64_t off, uint64_t len):
    v.vs_type = VS_STRING
    v.vs_off = off
    v.vs_len = len


PAGE_SIZE = 4096
PAGE_MASK = (PAGE_SIZE-1)
cdef uint64_t PAGE_ALIGN(uint64_t addr):
    return ((addr+PAGE_MASK) & ~PAGE_MASK)

    
def dim_count(loc):
    with open(loc) as f:
# XXX handle space as the vector in question
        for line in f:
            count = len(line.split(' '))
            break;
    return count

def word_len_count(loc):
    vector_count = 0
    word_len_total = 0
    with open(loc) as f:
        for line in f:
            # XXX handle space as the vector in question
            word_len_total += len(line.split(' ')[0]) + 1
            vector_count += 1
    return (word_len_total, vector_count)


def glove2bin(iloc, oloc):
    cdef int ofd
    vec_len = dim_count(iloc)
    word_len_total, linecount = word_len_count(iloc)

    # header + matrix
    filesize = PAGE_SIZE + PAGE_ALIGN(linecount*vec_len*sizeof(float))
    # vector norms
    filesize += PAGE_ALIGN(linecount*sizeof(float))
    # strings
    filesize += word_len_total
    of = open(oloc, "rw+")
    of.truncate(filesize)
    of.close()
    ofd = posix.fcntl.open(oloc, posix.fcntl.O_RDWR|posix.fcntl.O_CREAT, 0644)
    if ofd == -1:
        raise IOError("failed to open output file")
    f = open(iloc)
    vh = <vector_header*>mmap(NULL, filesize, PROT_READ|PROT_WRITE, MAP_SHARED, ofd, 0)
    init_vh(vh)
    vs = <vector_section*>&vh[1]
    init_vs_mat(vs, "GloVe vectors", PAGE_SIZE, vec_len*linecount*sizeof(float), VS_FLOAT32, linecount, vec_len);

    vs = &vs[1];
    off = PAGE_SIZE + PAGE_ALIGN(vec_len*linecount*sizeof(float));
    init_vs_vec(vs, "GloVe v-norms", off, linecount*sizeof(float), VS_FLOAT32, linecount);

    vs = &vs[1];
    off = off + PAGE_ALIGN(linecount*sizeof(float));
    init_vs_str(vs, "GloVe words", off, word_len_total);

    vector = <float *>PAGE_ALIGN(<uint64_t>&vs[1]);
    normvector = <float*>PAGE_ALIGN(<uint64_t>&vector[linecount*vec_len]);
    wordptr = <char *>PAGE_ALIGN(<uint64_t>&normvector[linecount]);

    id2word = np.empty( (linecount), dtype=str)
    id2glove = np.empty( (linecount, 300), dtype=np.float64)
    id2norm =  np.empty( (linecount), dtype=np.float64)
    i = 0
    # demarshal and then copy for the sake of simplicity
    with open(iloc) as f:
        for line in f:
            arr = line.split(" ")
            id2word[i] = arr[0]
            arr = arr[1:]
            arr = map(float, arr)
            id2glove[i] = np.asarray(arr, dtype=np.float64)
            id2norm[i] = np.linalg.norm(id2glove[i])
            id2glove[i] /= id2norm[i]
            i+= 1

    for i in xrange(linecount):
        ptr = <char *>id2word[i]
        strcpy(wordptr, ptr)
        wordptr += strlen(ptr) + 1
        normvector[i] = <float>id2norm[i]
        off = i*vec_len
        for j in xrange(vec_len):
            vector[off + j] = <float>id2glove[i][j]
