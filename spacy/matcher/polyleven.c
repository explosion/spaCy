/*
 * Adapted from Polyleven (https://ceptord.net/)
 *
 * Source: https://github.com/fujimotos/polyleven/blob/c3f95a080626c5652f0151a2e449963288ccae84/polyleven.c
 *
 * Copyright (c) 2021 Fujimoto Seiji <fujimoto@ceptord.net>
 * Copyright (c) 2021 Max Bachmann <kontakt@maxbachmann.de>
 * Copyright (c) 2022 Nick Mazuk
 * Copyright (c) 2022 Michael Weiss <code@mweiss.ch>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include <Python.h>
#include <stdint.h>

#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define MAX(a,b) ((a) > (b) ? (a) : (b))
#define CDIV(a,b) ((a) / (b) + ((a) % (b) > 0))
#define BIT(i,n) (((i) >> (n)) & 1)
#define FLIP(i,n) ((i) ^ ((uint64_t) 1 << (n)))
#define ISASCII(kd) ((kd) == PyUnicode_1BYTE_KIND)

/*
 * Bare bone of PyUnicode
 */
struct strbuf {
    void *ptr;
    int kind;
    int64_t len;
};

static void strbuf_init(struct strbuf *s, PyObject *o)
{
    s->ptr = PyUnicode_DATA(o);
    s->kind = PyUnicode_KIND(o);
    s->len = PyUnicode_GET_LENGTH(o);
}

#define strbuf_read(s, i) PyUnicode_READ((s)->kind, (s)->ptr, (i))

/*
 * An encoded mbleven model table.
 *
 * Each 8-bit integer represents an edit sequence, with using two
 * bits for a single operation.
 *
 *   01 = DELETE, 10 = INSERT, 11 = REPLACE
 *
 * For example, 13 is '1101' in binary notation, so it means
 * DELETE + REPLACE.
 */
static const uint8_t MBLEVEN_MATRIX[] = {
     3,   0,  0,  0,  0,  0,  0,  0,
     1,   0,  0,  0,  0,  0,  0,  0,
     15,  9,  6,  0,  0,  0,  0,  0,
     13,  7,  0,  0,  0,  0,  0,  0,
     5,   0,  0,  0,  0,  0,  0,  0,
     63, 39, 45, 57, 54, 30, 27,  0,
     61, 55, 31, 37, 25, 22,  0,  0,
     53, 29, 23,  0,  0,  0,  0,  0,
     21,  0,  0,  0,  0,  0,  0,  0,
};

#define MBLEVEN_MATRIX_GET(k, d) ((((k) + (k) * (k)) / 2 - 1) + (d)) * 8

static int64_t mbleven_ascii(char *s1, int64_t len1,
                             char *s2, int64_t len2, int k)
{
    int pos;
    uint8_t m;
    int64_t i, j, c, r;

    pos = MBLEVEN_MATRIX_GET(k, len1 - len2);
    r = k + 1;

    while (MBLEVEN_MATRIX[pos]) {
        m = MBLEVEN_MATRIX[pos++];
        i = j = c = 0;
        while (i < len1 && j < len2) {
            if (s1[i] != s2[j]) {
                c++;
                if (!m) break;
                if (m & 1) i++;
                if (m & 2) j++;
                m >>= 2;
            } else {
                i++;
                j++;
            }
        }
        c += (len1 - i) + (len2 - j);
        r = MIN(r, c);
        if (r < 2) {
            return r;
        }
    }
    return r;
}

static int64_t mbleven(PyObject *o1, PyObject *o2, int64_t k)
{
    int pos;
    uint8_t m;
    int64_t i, j, c, r;
    struct strbuf s1, s2;

    strbuf_init(&s1, o1);
    strbuf_init(&s2, o2);

    if (s1.len < s2.len)
        return mbleven(o2, o1, k);

    if (k > 3)
        return -1;

    if (k < s1.len - s2.len)
        return k + 1;

    if (ISASCII(s1.kind) && ISASCII(s2.kind))
        return mbleven_ascii(s1.ptr, s1.len, s2.ptr, s2.len, k);

    pos = MBLEVEN_MATRIX_GET(k, s1.len - s2.len);
    r = k + 1;

    while (MBLEVEN_MATRIX[pos]) {
        m = MBLEVEN_MATRIX[pos++];
        i = j = c = 0;
        while (i < s1.len && j < s2.len) {
            if (strbuf_read(&s1, i) != strbuf_read(&s2, j)) {
                c++;
                if (!m) break;
                if (m & 1) i++;
                if (m & 2) j++;
                m >>= 2;
            } else {
                i++;
                j++;
            }
        }
        c += (s1.len - i) + (s2.len - j);
        r = MIN(r, c);
        if (r < 2) {
            return r;
        }
    }
    return r;
}

/*
 * Data structure to store Peq (equality bit-vector).
 */
struct blockmap_entry {
    uint32_t key[128];
    uint64_t val[128];
};

struct blockmap {
    int64_t nr;
    struct blockmap_entry *list;
};

#define blockmap_key(c) ((c) | 0x80000000U)
#define blockmap_hash(c) ((c) % 128)

static int blockmap_init(struct blockmap *map, struct strbuf *s)
{
    int64_t i;
    struct blockmap_entry *be;
    uint32_t c, k;
    uint8_t h;

    map->nr = CDIV(s->len, 64);
    map->list = calloc(1,  map->nr * sizeof(struct blockmap_entry));
    if (map->list == NULL) {
        PyErr_NoMemory();
        return -1;
    }

    for (i = 0; i < s->len; i++) {
        be = &(map->list[i / 64]);
        c = strbuf_read(s, i);
        h = blockmap_hash(c);
        k = blockmap_key(c);

        while (be->key[h] && be->key[h] != k)
            h = blockmap_hash(h + 1);
        be->key[h] = k;
        be->val[h] |= (uint64_t) 1 << (i % 64);
    }
    return 0;
}

static void blockmap_clear(struct blockmap *map)
{
    if (map->list)
        free(map->list);
    map->list = NULL;
    map->nr = 0;
}

static uint64_t blockmap_get(struct blockmap *map, int block, uint32_t c)
{
    struct blockmap_entry *be;
    uint8_t h;
    uint32_t k;

    h = blockmap_hash(c);
    k = blockmap_key(c);

    be = &(map->list[block]);
    while (be->key[h] && be->key[h] != k)
        h = blockmap_hash(h + 1);
    return be->key[h] == k ? be->val[h] : 0;
}

/*
 * Myers' bit-parallel algorithm
 *
 * See: G. Myers. "A fast bit-vector algorithm for approximate string
 *      matching based on dynamic programming." Journal of the ACM, 1999.
 */
static int64_t myers1999_block(struct strbuf *s1, struct strbuf *s2,
                               struct blockmap *map)
{
    uint64_t Eq, Xv, Xh, Ph, Mh, Pv, Mv, Last;
    uint64_t *Mhc, *Phc;
    int64_t i, b, hsize, vsize, Score;
    uint8_t Pb, Mb;

    hsize = CDIV(s1->len, 64);
    vsize = CDIV(s2->len, 64);
    Score = s2->len;

    Phc = malloc(hsize * 2 * sizeof(uint64_t));
    if (Phc == NULL) {
        PyErr_NoMemory();
        return -1;
    }
    Mhc = Phc + hsize;
    memset(Phc, -1, hsize * sizeof(uint64_t));
    memset(Mhc, 0, hsize * sizeof(uint64_t));
    Last = (uint64_t)1 << ((s2->len - 1) % 64);

    for (b = 0; b < vsize; b++) {
        Mv = 0;
        Pv = (uint64_t) -1;
        Score = s2->len;

        for (i = 0; i < s1->len; i++) {
            Eq = blockmap_get(map, b, strbuf_read(s1, i));

            Pb = BIT(Phc[i / 64], i % 64);
            Mb = BIT(Mhc[i / 64], i % 64);

            Xv = Eq | Mv;
            Xh = ((((Eq | Mb) & Pv) + Pv) ^ Pv) | Eq | Mb;

            Ph = Mv | ~ (Xh | Pv);
            Mh = Pv & Xh;

            if (Ph & Last) Score++;
            if (Mh & Last) Score--;

            if ((Ph >> 63) ^ Pb)
                Phc[i / 64] = FLIP(Phc[i / 64], i % 64);

            if ((Mh >> 63) ^ Mb)
                Mhc[i / 64] = FLIP(Mhc[i / 64], i % 64);

            Ph = (Ph << 1) | Pb;
            Mh = (Mh << 1) | Mb;

            Pv = Mh | ~ (Xv | Ph);
            Mv = Ph & Xv;
        }
    }
    free(Phc);
    return Score;
}

static int64_t myers1999_simple(uint8_t *s1, int64_t len1, uint8_t *s2, int64_t len2)
{
    uint64_t Peq[256];
    uint64_t Eq, Xv, Xh, Ph, Mh, Pv, Mv, Last;
    int64_t i;
    int64_t Score = len2;

    memset(Peq, 0, sizeof(Peq));

    for (i = 0; i < len2; i++)
        Peq[s2[i]] |= (uint64_t) 1 << i;

    Mv = 0;
    Pv = (uint64_t) -1;
    Last = (uint64_t) 1 << (len2 - 1);

    for (i = 0; i < len1; i++) {
        Eq = Peq[s1[i]];

        Xv = Eq | Mv;
        Xh = (((Eq & Pv) + Pv) ^ Pv) | Eq;

        Ph = Mv | ~ (Xh | Pv);
        Mh = Pv & Xh;

        if (Ph & Last) Score++;
        if (Mh & Last) Score--;

        Ph = (Ph << 1) | 1;
        Mh = (Mh << 1);

        Pv = Mh | ~ (Xv | Ph);
        Mv = Ph & Xv;
    }
    return Score;
}

static int64_t myers1999(PyObject *o1, PyObject *o2)
{
    struct strbuf s1, s2;
    struct blockmap map;
    int64_t ret;

    strbuf_init(&s1, o1);
    strbuf_init(&s2, o2);

    if (s1.len < s2.len)
        return myers1999(o2, o1);

    if (ISASCII(s1.kind) && ISASCII(s2.kind) && s2.len < 65)
        return myers1999_simple(s1.ptr, s1.len, s2.ptr, s2.len);

    if (blockmap_init(&map, &s2))
        return -1;

    ret = myers1999_block(&s1, &s2, &map);
    blockmap_clear(&map);
    return ret;
}

/*
 * Interface functions
 */
static int64_t polyleven(PyObject *o1, PyObject *o2, int64_t k)
{
    int64_t len1, len2;

    len1 = PyUnicode_GET_LENGTH(o1);
    len2 = PyUnicode_GET_LENGTH(o2);

    if (len1 < len2)
        return polyleven(o2, o1, k);

    if (k == 0)
        return PyUnicode_Compare(o1, o2) ? 1 : 0;

    if (0 < k && k < len1 - len2)
        return k + 1;

    if (len2 == 0)
        return len1;

    if (0 < k && k < 4)
        return mbleven(o1, o2, k);

    return myers1999(o1, o2);
}
