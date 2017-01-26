import numpy as np
from ctypes import c_char_p

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

cdef extern from "sys/stat.h":
    cdef struct stat:
        off_t st_size
    int fstat(int fildes, stat *buf)

cdef extern from "string.h":
    size_t strlen(const char *s)
    char *strcpy(char *dest, const char *src);
           
cdef void init_vh(vector_header *v, int type, int nsections):
    v.vh_magic =  VH_MAGIC
    v.vh_version = VH_GLOVE_VERSION
    v.vh_type = type
    v.vh_nsections = nsections

cdef void init_vs_mat(vector_section *v, char *name, uint64_t off, uint64_t len, uint8_t precision, uint32_t m, uint32_t n):
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
        count = 0
        for line in f:
            count = len(line.split(' ')) - 1
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


cdef vector_header *vec_save_setup(char *oloc, uint32_t filesize, int type, int nsections):
    cdef int ofd
    with open(oloc, "w+") as f:
        f.truncate(filesize)
    ofd = posix.fcntl.open(oloc, posix.fcntl.O_RDWR|posix.fcntl.O_CREAT, 0644)
    if ofd == -1:
        raise IOError("failed to open output file")
    vh = <vector_header*>mmap(NULL, filesize, PROT_READ|PROT_WRITE, MAP_SHARED, ofd, 0)
    close(ofd)
    init_vh(vh, type, nsections)
    return vh

cdef vector_header *vec_load_setup(iloc):
    cdef int ifd
    cdef stat sb
    ifd = posix.fcntl.open(iloc, posix.fcntl.O_RDONLY)
    if ifd == -1:
        raise IOError("failed to open input file")
    fstat(ifd, &sb)
    vh = <vector_header*>mmap(NULL, sb.st_size, PROT_READ, MAP_SHARED, ifd, 0)
    close(ifd)
    if vh.vh_magic != VH_MAGIC:
        raise IOError("invalid file type")
    if vh.vh_version != VH_GLOVE_VERSION:
        raise IOError("version mismatch")
    vs = <vector_section*>&vh[1]
    return vh

def vec2bin(iloc, oloc, nlines):
    word_len_total, linecount = word_len_count(iloc)
    vec_len = dim_count(iloc)
    if nlines > linecount:
        print "%d vectors requested only %d available"%(nlines, linecount)
    else:
        linecount = nlines
    id2word = np.empty( (linecount), dtype=object)
    id2glove = np.empty( (linecount, vec_len), dtype=np.float64)
    id2norm =  np.empty( (linecount), dtype=np.float64)
    # demarshal text 
    with open(iloc) as f:
        i = 0
        for line in f:
            arr = line.split(" ")
            id2word[i] = arr[0]
            arr = arr[1:]
            arr = map(float, arr)
            id2glove[i] = np.asarray(arr, dtype=np.float64)
            id2norm[i] = np.linalg.norm(id2glove[i])
            id2glove[i] /= id2norm[i]
            i+= 1

    # header + matrix
    filesize = PAGE_SIZE + PAGE_ALIGN(linecount*vec_len*sizeof(float))
    # vector norms
    filesize += PAGE_ALIGN(linecount*sizeof(float))
    # strings
    filesize += word_len_total

    # map file and initialize section headers
    vh = vec_save_setup(oloc, filesize, VH_TYPE_GLOVE, 3)
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

    # copy data to packed binary format
    for i in xrange(linecount):
        # copy ith word and advance dst pointer
        # past its terminating null
        ptr = c_char_p(id2word[i]).value
        strcpy(wordptr, ptr)
        wordptr += strlen(ptr) + 1

        normvector[i] = <float>id2norm[i]
        off = i*vec_len
        for j in xrange(vec_len):
            vector[off + j] = <float>id2glove[i][j]
    munmap(vh, filesize)
