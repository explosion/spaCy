#ifndef GLOVE2BIN_H_
#define GLOVE2BIN_H_

#define VH_MAGIC  0xF00EBEEFCAFEBABE

#define VH_TYPE_GLOVE   1          /* binary representation of glove vectors */
#define VH_TYPE_CLUSTER 2          /* binary representation of clusters */
#define VH_TYPE_DOC     3          /* binary representation of document post-embed */

struct vector_header {
    uint64_t vh_magic;
    uint32_t vh_version;
    uint16_t vh_type;
    uint16_t vh_nsections;
};

#define VH_GLOVE_VERSION 20170123
#define VS_MAXNAMELEN 16

#define VS_FLOAT8	1
#define VS_FLOAT16	2
#define VS_FLOAT32	4
#define VS_FLOAT64	8

#define VS_VECTOR	1
#define VS_MATRIX	2
#define VS_STRING	3

struct vector_section {
    char     vs_name[VS_MAXNAMELEN];
    uint64_t vs_off;
    uint64_t vs_len;
    uint8_t  vs_type;      /* 1: vector 2: matrix 3: strings */
    uint8_t  vs_precision; /* 1: float8 2: float16 4: float32 8: float64 */
    uint8_t  vs_pad[2];
    uint32_t vs_dims[3];  /* rows/columns/z */
};

#endif
