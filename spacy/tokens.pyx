# cython: profile=True
from .lexeme cimport *
cimport cython

DEF PADDING = 5

cdef int bounds_check(int i, int length, int padding) except -1:
    if (i + padding) < 0:
        raise IndexError
    if (i - padding) >= length:
        raise IndexError


cdef class Tokens:
    """A sequence of references to Lexeme objects.

    The Tokens class provides fast and memory-efficient access to lexical features,
    and can efficiently export the data to a numpy array.  Specific languages
    create their own Tokens subclasses, to provide more convenient access to
    language-specific features.

    >>> from spacy.en import EN
    >>> tokens = EN.tokenize('An example sentence.')
    >>> tokens.string(0)
    'An'
    >>> tokens.prob(0) > tokens.prob(1)
    True
    >>> tokens.can_noun(0)
    False
    >>> tokens.can_noun(1)
    True
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
        self._lex_ptr = <Lexeme**>self.mem.alloc(size + (PADDING*2), sizeof(Lexeme*))
        self._idx_ptr = <int*>self.mem.alloc(size + (PADDING*2), sizeof(int))
        self._pos_ptr = <int*>self.mem.alloc(size + (PADDING*2), sizeof(int))
        self.lex = self._lex_ptr
        self.idx = self._idx_ptr
        self.pos = self._pos_ptr
        cdef int i
        for i in range(size + (PADDING*2)):
            self.lex[i] = &EMPTY_LEXEME
        self.lex += PADDING
        self.idx += PADDING
        self.pos += PADDING
        self.max_length = size
        self.length = 0

    def __getitem__(self, i):
        bounds_check(i, self.length, PADDING)
        return Token(self._string_store, i, self.idx[i], self.pos[i], self.lex[i][0])

    def __len__(self):
        return self.length

    cdef int push_back(self, int idx, Lexeme* lexeme) except -1:
        if self.length == self.max_length:
            self._realloc(self.length * 2)
        self.lex[self.length] = lexeme
        self.idx[self.length] = idx
        self.pos[self.length] = 0
        self.length += 1
        return idx + lexeme.length

    cdef int extend(self, int idx, Lexeme** lexemes, int n) except -1:
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

    def _realloc(self, new_size):
        self.max_length = new_size
        n = new_size + (PADDING * 2)
        self._lex_ptr = <Lexeme**>self.mem.realloc(self._lex_ptr, n * sizeof(Lexeme*))
        self._idx_ptr = <int*>self.mem.realloc(self._idx_ptr, n * sizeof(int))
        self._pos_ptr = <int*>self.mem.realloc(self._pos_ptr, n * sizeof(int))
        self.lex = self._lex_ptr + PADDING
        self.idx = self._idx_ptr + PADDING
        self.pos = self._pos_ptr + PADDING
        for i in range(self.length, self.max_length + PADDING):
            self.lex[i] = &EMPTY_LEXEME


@cython.freelist(64)
cdef class Token:
    def __init__(self, StringStore string_store, int i, int idx, int pos, dict lex):
        self._string_store = string_store
        self.idx = idx
        self.pos = pos
        self.i = i
        self.id = lex['id']
        
        self.cluster = lex['cluster']
        self.length = lex['length']
        self.postype = lex['postype']
        self.sensetype = lex['supersense']
        self.sic = lex['sic']
        self.norm = lex['norm']
        self.shape = lex['shape']
        self.vocab10k = lex['vocab10k']
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

