# cython: profile=True
from .word cimport Lexeme

from .lexeme cimport *
cimport numpy
cimport cython
import numpy

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
    def __init__(self, string_length=0):
        if string_length >= 3:
            size = int(string_length / 3.0)
        else:
            size = 5
        self.mem = Pool()
        # Guarantee self.lex[i-x], for any i >= 0 and x < padding is in bounds
        # However, we need to remember the true starting places, so that we can
        # realloc.
        self._lex_ptr = <LexemeC**>self.mem.alloc(size + (PADDING*2), sizeof(LexemeC*))
        self._idx_ptr = <int*>self.mem.alloc(size + (PADDING*2), sizeof(int))
        self._pos_ptr = <int*>self.mem.alloc(size + (PADDING*2), sizeof(int))
        self.lex = self._lex_ptr
        self.idx = self._idx_ptr
        self.pos = self._pos_ptr
        for i in range(PADDING):
            self.lex[i] = &EMPTY_LEXEME
        for i in range(size, PADDING):
            self.lex[i] = &EMPTY_LEXEME
        self.lex += PADDING
        self.idx += PADDING
        self.pos += PADDING

        self.max_length = size
        self.length = 0

    def __getitem__(self, i):
        bounds_check(i, self.length, PADDING)
        return Lexeme(<size_t>self.lex[i])

    def __len__(self):
        return self.length

    cdef int push_back(self, int idx, LexemeC* lexeme) except -1:
        if self.length == self.max_length:
            self._realloc(self.length * 2)
        self.lex[self.length] = lexeme
        self.idx[self.length] = idx
        self.pos[self.length] = 0
        self.length += 1
        return idx + lexeme.ints[<int>LexInt_length]

    def _realloc(self, new_size):
        self.max_length = new_size
        n = new_size + (PADDING * 2)
        self._lex_ptr = <LexemeC**>self.mem.realloc(self._lex_ptr, n * sizeof(LexemeC*))
        self._idx_ptr = <int*>self.mem.realloc(self._idx_ptr, n * sizeof(int))
        self._pos_ptr = <int*>self.mem.realloc(self._pos_ptr, n * sizeof(int))
        self.lex = self._lex_ptr + PADDING
        self.idx = self._idx_ptr + PADDING
        self.pos = self._pos_ptr + PADDING


    cdef int extend(self, int idx, LexemeC** lexemes, int n) except -1:
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

    cpdef int id(self, size_t i) except -1:
        bounds_check(i, self.length, PADDING)
        return self.lex[i].ints[<int>LexInt_id]

    cpdef float prob(self, size_t i) except 1:
        bounds_check(i, self.length, PADDING)
        return self.lex[i].floats[<int>LexFloat_prob]

    cpdef int cluster(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return self.lex[i].ints[<int>LexInt_cluster]

    cpdef bint check_orth_flag(self, size_t i, size_t flag_id) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_orth_flag(self.lex[i], flag_id)

    cpdef bint check_dist_flag(self, size_t i, size_t flag_id) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], flag_id)

    cpdef unicode string_view(self, size_t i, size_t view_id):
        bounds_check(i, self.length, PADDING)
        return lexeme_get_string(self.lex[i], view_id)

    # Provide accessor methods for the features supported by the language.
    # Without these, clients have to use the underlying string_view and check_flag
    # methods, which requires them to know the IDs.

    cpdef unicode string(self, size_t i):
        bounds_check(i, self.length, PADDING)
        return self.orig(i)

    cpdef unicode orig(self, size_t i):
        bounds_check(i, self.length, PADDING)
        cdef bytes utf8_string = self.lex[i].strings[<int>LexStr_orig]
        cdef unicode string = utf8_string.decode('utf8')
        return string

    cpdef unicode norm(self, size_t i):
        bounds_check(i, self.length, PADDING)
        cdef bytes utf8_string = self.lex[i].strings[<int>LexStr_norm]
        cdef unicode string = utf8_string.decode('utf8')
        return string

    cpdef unicode shape(self, size_t i):
        bounds_check(i, self.length, PADDING)
        return lexeme_get_string(self.lex[i], LexStr_shape)

    cpdef unicode unsparse(self, size_t i):
        bounds_check(i, self.length, PADDING)
        return lexeme_get_string(self.lex[i], LexStr_unsparse)

    cpdef unicode asciied(self, size_t i):
        bounds_check(i, self.length, PADDING)
        return lexeme_get_string(self.lex[i], LexStr_asciied)

    cpdef bint is_alpha(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_orth_flag(self.lex[i], LexOrth_alpha)

    cpdef bint is_ascii(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_orth_flag(self.lex[i], LexOrth_ascii)

    cpdef bint is_digit(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_orth_flag(self.lex[i], LexOrth_digit)

    cpdef bint is_lower(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_orth_flag(self.lex[i], LexOrth_lower)

    cpdef bint is_punct(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_orth_flag(self.lex[i], LexOrth_punct)

    cpdef bint is_space(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_orth_flag(self.lex[i], LexOrth_space)

    cpdef bint is_title(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_orth_flag(self.lex[i], LexOrth_title)

    cpdef bint is_upper(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_orth_flag(self.lex[i], LexOrth_upper)

    cpdef bint can_adj(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_adj)

    cpdef bint can_adp(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_adp)

    cpdef bint can_adv(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_adv)

    cpdef bint can_conj(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_conj)

    cpdef bint can_det(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_det)

    cpdef bint can_noun(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_noun)

    cpdef bint can_num(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_num)

    cpdef bint can_pdt(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_pdt)

    cpdef bint can_pos(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_pos)

    cpdef bint can_pron(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_pron)

    cpdef bint can_prt(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_prt)

    cpdef bint can_punct(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_punct)

    cpdef bint can_verb(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_verb)

    cpdef bint oft_lower(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_lower)

    cpdef bint oft_title(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_title)

    cpdef bint oft_upper(self, size_t i) except *:
        bounds_check(i, self.length, PADDING)
        return lexeme_check_dist_flag(self.lex[i], LexDist_upper)
