# cython: profile=True
from .word cimport Lexeme

from .lexeme cimport *


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
    def __cinit__(self, string_length=0):
        size = int(string_length / 3) if string_length >= 3 else 1
        self.v = new vector[LexemeC*]()
        self.v.reserve(size)

    def __getitem__(self, i):
        return Lexeme(<size_t>self.v.at(i))

    def __len__(self):
        return self.v.size()

    def __dealloc__(self):
        del self.v

    def append(self, Lexeme lexeme):
        self.v.push_back(lexeme._c)

    cpdef int id(self, size_t i) except -1:
        return self.v.at(i).ints[<int>LexInt_i]

    cpdef unicode string(self, size_t i):
        cdef bytes utf8_string = self.v.at(i).strings[<int>LexStr_orig]
        cdef unicode string = utf8_string.decode('utf8')
        return string

    cpdef float prob(self, size_t i) except 1:
        return self.v.at(i).floats[<int>LexFloat_prob]

    cpdef int cluster(self, size_t i) except *:
        return self.v.at(i).ints[<int>LexInt_cluster]

    cpdef bint check_orth_flag(self, size_t i, size_t flag_id) except *:
        return lexeme_check_orth_flag(self.v.at(i), flag_id)

    cpdef bint check_dist_flag(self, size_t i, size_t flag_id) except *:
        return lexeme_check_dist_flag(self.v.at(i), flag_id)

    cpdef unicode string_view(self, size_t i, size_t view_id):
        return lexeme_get_string(self.v.at(i), view_id)

    # Provide accessor methods for the features supported by the language.
    # Without these, clients have to use the underlying string_view and check_flag
    # methods, which requires them to know the IDs.
    cpdef unicode casefix(self, size_t i):
        return lexeme_get_string(self.v.at(i), LexStr_casefix)

    cpdef unicode shape(self, size_t i):
        return lexeme_get_string(self.v.at(i), LexStr_shape)

    cpdef unicode unsparse(self, size_t i):
        return lexeme_get_string(self.v.at(i), LexStr_unsparse)

    cpdef unicode asciied(self, size_t i):
        return lexeme_get_string(self.v.at(i), LexStr_asciied)

    cpdef bint is_alpha(self, size_t i) except *:
        return lexeme_check_orth_flag(self.v.at(i), LexOrth_alpha)

    cpdef bint is_ascii(self, size_t i) except *:
        return lexeme_check_orth_flag(self.v.at(i), LexOrth_ascii)

    cpdef bint is_digit(self, size_t i) except *:
        return lexeme_check_orth_flag(self.v.at(i), LexOrth_digit)

    cpdef bint is_lower(self, size_t i) except *:
        return lexeme_check_orth_flag(self.v.at(i), LexOrth_lower)

    cpdef bint is_punct(self, size_t i) except *:
        return lexeme_check_orth_flag(self.v.at(i), LexOrth_punct)

    cpdef bint is_space(self, size_t i) except *:
        return lexeme_check_orth_flag(self.v.at(i), LexOrth_space)

    cpdef bint is_title(self, size_t i) except *:
        return lexeme_check_orth_flag(self.v.at(i), LexOrth_title)

    cpdef bint is_upper(self, size_t i) except *:
        return lexeme_check_orth_flag(self.v.at(i), LexOrth_upper)

    cpdef bint can_adj(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_adj)

    cpdef bint can_adp(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_adp)

    cpdef bint can_adv(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_adv)

    cpdef bint can_conj(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_conj)

    cpdef bint can_det(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_det)

    cpdef bint can_noun(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_noun)

    cpdef bint can_num(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_num)

    cpdef bint can_pdt(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_pdt)

    cpdef bint can_pos(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_pos)

    cpdef bint can_pron(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_pron)

    cpdef bint can_prt(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_prt)

    cpdef bint can_punct(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_punct)

    cpdef bint can_verb(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_verb)

    cpdef bint oft_lower(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_lower)

    cpdef bint oft_title(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_title)

    cpdef bint oft_upper(self, size_t i) except *:
        return lexeme_check_dist_flag(self.v.at(i), LexDist_upper)
