from spacy.lexeme cimport LexemeC
from libcpp.vector cimport vector
from thinc.typedefs cimport atom_t


cdef class Tokens:
    cdef vector[LexemeC*] *lex
    cdef vector[int] *idx
    cdef vector[int] *pos

    cdef int extend(self, int i, LexemeC** lexemes, int n) except -1
    cdef int push_back(self, int i, LexemeC* lexeme) except -1
    cdef int int_array(self, atom_t* atoms, int i, int* indices, int n_idx,
                       int* features, int n_feat) except -1
    cdef int string_array(self, atom_t* atoms, int i, int* indices, int n_idx,
                          int* features, int n_feat) except -1
    cdef int bool_array(self, atom_t* atoms, int i, int* indices, int n_idx,
                        int* features, int n_feat) except -1

    cpdef int id(self, size_t i) except -1
    cpdef float prob(self, size_t i) except 1
    cpdef int cluster(self, size_t i) except *
    cpdef bint check_orth_flag(self, size_t i, size_t flag_id) except *
    cpdef bint check_dist_flag(self, size_t i, size_t flag_id) except *
    cpdef unicode string_view(self, size_t i, size_t view_id)

    cpdef unicode string(self, size_t i)
    cpdef unicode orig(self, size_t i)
    cpdef unicode norm(self, size_t i)
    cpdef unicode shape(self, size_t i)
    cpdef unicode unsparse(self, size_t i)
    cpdef unicode asciied(self, size_t i)
    cpdef bint is_alpha(self, size_t i) except *
    cpdef bint is_ascii(self, size_t i) except * 
    cpdef bint is_digit(self, size_t i) except *
    cpdef bint is_lower(self, size_t i) except *
    cpdef bint is_punct(self, size_t i) except *
    cpdef bint is_space(self, size_t i) except *
    cpdef bint is_title(self, size_t i) except *
    cpdef bint is_upper(self, size_t i) except *
    cpdef bint can_adj(self, size_t i) except *
    cpdef bint can_adp(self, size_t i) except *
    cpdef bint can_adv(self, size_t i) except *
    cpdef bint can_conj(self, size_t i) except *
    cpdef bint can_det(self, size_t i) except *
    cpdef bint can_noun(self, size_t i) except *
    cpdef bint can_num(self, size_t i) except *
    cpdef bint can_pdt(self, size_t i) except *
    cpdef bint can_pos(self, size_t i) except *
    cpdef bint can_pron(self, size_t i) except *
    cpdef bint can_prt(self, size_t i) except *
    cpdef bint can_punct(self, size_t i) except *
    cpdef bint can_verb(self, size_t i) except *
    cpdef bint oft_lower(self, size_t i) except *
    cpdef bint oft_title(self, size_t i) except *
    cpdef bint oft_upper(self, size_t i) except *
