from libc.stdint cimport uint8_t, uint16_t 
from libc.stdint cimport uint32_t, int32_t
from libc.stdint cimport uint64_t

cdef enum:
    VS_NIL
    VS_VECTOR
    VS_MATRIX
    VS_STRING
    VH_MAGIC = 0xF00EBEEFCAFEBABE
    VH_GLOVE_VERSION = 20170123
    VS_MAXNAMELEN =16
    VS_FLOAT8  = 1
    VS_FLOAT16 = 2
    VS_FLOAT32 = 4
    VS_FLOAT64 = 8
    VH_TYPE_GLOVE = 1
    VH_TYPE_DOC = 2

cdef struct vector_header:
    uint64_t vh_magic
    uint32_t vh_version
    uint16_t vh_type
    uint16_t vh_nsections

cdef struct vector_section:
    char     vs_name[VS_MAXNAMELEN]
    uint64_t vs_off
    uint64_t vs_len
    uint8_t  vs_type
    uint8_t  vs_precision
    uint16_t vs_pad
    uint32_t vs_dims[3]


cdef vector_header *vec_save_setup(char *oloc, uint32_t filesize, int type, int nsections)
cdef vector_header *vec_load_setup(iloc)
