# cython: profile=True
from preshed.maps cimport PreshMap
from preshed.counter cimport PreshCounter

from .lexeme cimport *
cimport cython

import numpy as np
cimport numpy as np

POS = 0
ENTITY = 0

DEF PADDING = 5


cdef int bounds_check(int i, int length, int padding) except -1:
    if (i + padding) < 0:
        raise IndexError
    if (i - padding) >= length:
        raise IndexError


cdef class Tokens:
    """A sequence of references to Lexeme objects.

    The Tokens class provides fast and memory-efficient access to lexical features,
    and can efficiently export the data to a numpy array.

    >>> from spacy.en import EN
    >>> tokens = EN.tokenize('An example sentence.')
    """
    def __init__(self, StringStore string_store, string_length=0):
        self._string_store = string_store
        if string_length >= 3:
            size = int(string_length / 3.0)
        else:
            size = 5
        self.mem = Pool()
        # Guarantee self.lex[i-x], for any i >= 0 and x < padding is in bounds
        # However, we need to remember the true starting places, so that we can
        # realloc.
        self._lex_ptr = <const Lexeme**>self.mem.alloc(size + (PADDING*2), sizeof(Lexeme*))
        self._idx_ptr = <int*>self.mem.alloc(size + (PADDING*2), sizeof(int))
        self._pos_ptr = <int*>self.mem.alloc(size + (PADDING*2), sizeof(int))
        self._ner_ptr = <int*>self.mem.alloc(size + (PADDING*2), sizeof(int))
        self.lex = self._lex_ptr
        self.idx = self._idx_ptr
        self.pos = self._pos_ptr
        self.ner = self._ner_ptr
        cdef int i
        for i in range(size + (PADDING*2)):
            self.lex[i] = &EMPTY_LEXEME
        self.lex += PADDING
        self.idx += PADDING
        self.pos += PADDING
        self.ner += PADDING
        self.max_length = size
        self.length = 0

    def __getitem__(self, i):
        bounds_check(i, self.length, PADDING)
        return Token(self._string_store, i, self.idx[i], self.pos[i], self.ner[i],
                     self.lex[i][0])

    def __iter__(self):
        for i in range(self.length):
            yield self[i]

    def __len__(self):
        return self.length

    cdef int push_back(self, int idx, const Lexeme* lexeme) except -1:
        if self.length == self.max_length:
            self._realloc(self.length * 2)
        self.lex[self.length] = lexeme
        self.idx[self.length] = idx
        self.pos[self.length] = 0
        self.ner[self.length] = 0
        self.length += 1
        return idx + lexeme.length

    cdef int extend(self, int idx, const Lexeme* const* lexemes, int n) except -1:
        cdef int i
        if lexemes == NULL:
            return idx
        elif n == 0:
            i = 0
            while lexemes[i] != NULL:
                idx = self.push_back(idx, lexemes[i])
                i += 1
        else:
            for i in range(n):
                idx = self.push_back(idx, lexemes[i])
        return idx

    cpdef int set_tag(self, int i, int tag_type, int tag) except -1:
        if tag_type == POS:
            self.pos[i] = tag
        elif tag_type == ENTITY:
            self.ner[i] = tag

    @cython.boundscheck(False)
    cpdef np.ndarray[long, ndim=2] get_array(self, list attr_ids):
        cdef int i, j
        cdef attr_id_t feature
        cdef np.ndarray[long, ndim=2] output
        output = np.ndarray(shape=(self.length, len(attr_ids)), dtype=int)
        for i in range(self.length):
            for j, feature in enumerate(attr_ids):
                output[i, j] = get_attr(self.lex[i], feature)
        return output

    def count_by(self, attr_id_t attr_id):
        cdef int i
        cdef attr_t attr
        cdef size_t count

        cdef PreshCounter counts = PreshCounter(2 ** 8)
        for i in range(self.length):
            attr = get_attr(self.lex[i], attr_id)
            counts.inc(attr, 1)
        return dict(counts)

    def _realloc(self, new_size):
        self.max_length = new_size
        n = new_size + (PADDING * 2)
        self._lex_ptr = <const Lexeme**>self.mem.realloc(self._lex_ptr, n * sizeof(Lexeme*))
        self._idx_ptr = <int*>self.mem.realloc(self._idx_ptr, n * sizeof(int))
        self._pos_ptr = <int*>self.mem.realloc(self._pos_ptr, n * sizeof(int))
        self._ner_ptr = <int*>self.mem.realloc(self._ner_ptr, n * sizeof(int))
        self.lex = self._lex_ptr + PADDING
        self.idx = self._idx_ptr + PADDING
        self.pos = self._pos_ptr + PADDING
        self.ner = self._ner_ptr + PADDING
        for i in range(self.length, self.max_length + PADDING):
            self.lex[i] = &EMPTY_LEXEME


@cython.freelist(64)
cdef class Token:
    def __init__(self, StringStore string_store, int i, int idx, int pos, int ner,
                 dict lex):
        self._string_store = string_store
        self.idx = idx
        self.pos = pos
        self.ner = ner
        self.i = i
        self.id = lex['id']
        
        self.cluster = lex['cluster']
        self.length = lex['length']
        self.postype = lex['pos_type']
        self.sensetype = lex['sense_type']
        self.sic = lex['sic']
        self.norm = lex['dense']
        self.shape = lex['shape']
        self.suffix = lex['asciied']
        self.prefix = lex['prefix']

        self.prob = lex['prob']
        self.flags = lex['flags']

    property string:
        def __get__(self):
            if self.sic == 0:
                return ''
            cdef bytes utf8string = self._string_store[self.sic]
            return utf8string.decode('utf8')
