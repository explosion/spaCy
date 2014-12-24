# cython: profile=True
from preshed.maps cimport PreshMap
from preshed.counter cimport PreshCounter

from .vocab cimport EMPTY_LEXEME
from .typedefs cimport attr_id_t, attr_t
from .typedefs cimport LEMMA
from .typedefs cimport ID, SIC, DENSE, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER, POS_TYPE
from .typedefs cimport POS, LEMMA

cimport cython

import numpy as np
cimport numpy as np


DEF PADDING = 5


cdef int bounds_check(int i, int length, int padding) except -1:
    if (i + padding) < 0:
        raise IndexError
    if (i - padding) >= length:
        raise IndexError


cdef attr_t get_token_attr(const TokenC* token, attr_id_t feat_name) nogil:
    if feat_name == LEMMA:
        return token.lemma
    elif feat_name == POS:
        return token.pos
    else:
        return get_lex_attr(token.lex, feat_name)


cdef attr_t get_lex_attr(const Lexeme* lex, attr_id_t feat_name) nogil:
    if feat_name < (sizeof(flags_t) * 8):
        return check_flag(lex, feat_name)
    elif feat_name == ID:
        return lex.id
    elif feat_name == SIC:
        return lex.sic
    elif feat_name == DENSE:
        return lex.dense
    elif feat_name == SHAPE:
        return lex.shape
    elif feat_name == PREFIX:
        return lex.prefix
    elif feat_name == SUFFIX:
        return lex.suffix
    elif feat_name == LENGTH:
        return lex.length
    elif feat_name == CLUSTER:
        return lex.cluster
    elif feat_name == POS_TYPE:
        return lex.pos_type
    else:
        return 0


cdef class Tokens:
    """A sequence of references to Lexeme objects.

    The Tokens class provides fast and memory-efficient access to lexical features,
    and can efficiently export the data to a numpy array.

    >>> from spacy.en import EN
    >>> tokens = EN.tokenize('An example sentence.')
    """
    def __init__(self, Vocab vocab, string_length=0):
        self.vocab = vocab
        if string_length >= 3:
            size = int(string_length / 3.0)
        else:
            size = 5
        self.mem = Pool()
        # Guarantee self.lex[i-x], for any i >= 0 and x < padding is in bounds
        # However, we need to remember the true starting places, so that we can
        # realloc.
        data_start = <TokenC*>self.mem.alloc(size + (PADDING*2), sizeof(TokenC))
        cdef int i
        for i in range(size + (PADDING*2)):
            data_start[i].lex = &EMPTY_LEXEME
        self.data = data_start + PADDING
        self.max_length = size
        self.length = 0

    def __getitem__(self, i):
        bounds_check(i, self.length, PADDING)
        return Token(self, i)

    def __iter__(self):
        for i in range(self.length):
            yield self[i]

    def __len__(self):
        return self.length

    cdef int push_back(self, int idx, LexemeOrToken lex_or_tok) except -1:
        if self.length == self.max_length:
            self._realloc(self.length * 2)
        cdef TokenC* t = &self.data[self.length]
        if LexemeOrToken is TokenC_ptr:
            t[0] = lex_or_tok[0]
        else:
            t.lex = lex_or_tok
        t.idx = idx
        self.length += 1
        return idx + t.lex.length

    @cython.boundscheck(False)
    cpdef np.ndarray[long, ndim=2] to_array(self, object attr_ids):
        cdef int i, j
        cdef attr_id_t feature
        cdef np.ndarray[long, ndim=2] output
        output = np.ndarray(shape=(self.length, len(attr_ids)), dtype=int)
        for i in range(self.length):
            for j, feature in enumerate(attr_ids):
                output[i, j] = get_token_attr(&self.data[i], feature)
        return output

    def count_by(self, attr_id_t attr_id):
        cdef int i
        cdef attr_t attr
        cdef size_t count

        cdef PreshCounter counts = PreshCounter(2 ** 8)
        for i in range(self.length):
            attr = get_token_attr(&self.data[i], attr_id)
            counts.inc(attr, 1)
        return dict(counts)

    def _realloc(self, new_size):
        self.max_length = new_size
        n = new_size + (PADDING * 2)
        # What we're storing is a "padded" array. We've jumped forward PADDING
        # places, and are storing the pointer to that. This way, we can access
        # words out-of-bounds, and get out-of-bounds markers.
        # Now that we want to realloc, we need the address of the true start,
        # so we jump the pointer back PADDING places.
        cdef TokenC* data_start = self.data - PADDING
        data_start = <TokenC*>self.mem.realloc(data_start, n * sizeof(TokenC))
        self.data = data_start + PADDING
        cdef int i
        for i in range(self.length, self.max_length + PADDING):
            self.data[i].lex = &EMPTY_LEXEME


@cython.freelist(64)
cdef class Token:
    def __init__(self, Tokens tokens, int i):
        self._seq = tokens
        self.i = i

    def __unicode__(self):
        cdef const TokenC* t = &self._seq.data[self.i]
        cdef int end_idx = t.idx + t.lex.length
        if self.i + 1 == self._seq.length:
            return self.string
        if end_idx == t[1].idx:
            return self.string
        else:
            return self.string + ' '

    def __len__(self):
        return self._seq.data[self.i].lex.length

    property idx:
        def __get__(self):
            return self._seq.data[self.i].idx

    property length:
        def __get__(self):
            return self._seq.data[self.i].lex.length

    property cluster:
        def __get__(self):
            return self._seq.data[self.i].lex.cluster

    property string:
        def __get__(self):
            cdef const TokenC* t = &self._seq.data[self.i]
            if t.lex.sic == 0:
                return ''
            cdef bytes utf8string = self._seq.vocab.strings[t.lex.sic]
            return utf8string.decode('utf8')

    property lemma:
        def __get__(self):
            cdef const TokenC* t = &self._seq.data[self.i]
            if t.lemma == 0:
                return self.string
            cdef bytes utf8string = self._seq.vocab.strings[t.lemma]
            return utf8string.decode('utf8')

    property dep:
        def __get__(self):
            return self._seq.data[self.i].dep_tag

    property pos:
        def __get__(self):
            return self._seq.data[self.i].pos

    property fine_pos:
        def __get__(self):
            return self._seq.data[self.i].fine_pos

    property sic:
        def __get__(self):
            return self._seq.data[self.i].lex.sic

    property head:
        def __get__(self):
            cdef const TokenC* t = &self._seq.data[self.i]
            return Token(self._seq, self.i + t.head)
