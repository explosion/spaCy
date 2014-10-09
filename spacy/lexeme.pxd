from .typedefs cimport hash_t, utf8_t, flag_t, id_t
from cymem.cymem cimport Pool


cpdef flag_t OOV_DIST_FLAGS


cpdef enum LexInts:
    LexInt_i
    LexInt_length
    LexInt_cluster
    LexInt_pos
    LexInt_supersense
    LexInt_N


cpdef enum LexFloats:
    LexFloat_prob
    LexFloat_sentiment
    LexFloat_N


cpdef enum LexStrs:
    LexStr_key
    LexStr_casefix
    LexStr_shape
    LexStr_unsparse
    LexStr_asciied
    LexStr_N


cpdef enum LexOrthFlags:
    LexOrth_alpha
    LexOrth_ascii
    LexOrth_digit
    LexOrth_lower
    LexOrth_punct
    LexOrth_space
    LexOrth_title
    LexOrth_upper
    LexOrth_N


cpdef enum LexDistFlags:
    LexDist_adj
    LexDist_adp
    LexDist_adv
    LexDist_conj
    LexDist_det
    LexDist_noun
    LexDist_num
    LexDist_pdt
    LexDist_pos
    LexDist_pron
    LexDist_prt
    LexDist_punct
    LexDist_verb

    LexDist_lower
    LexDist_title
    LexDist_upper

    LexDist_N


cdef struct LexemeC:
    int[<int>LexInt_N] ints
    float[<int>LexFloat_N] floats
    utf8_t[<int>LexStr_N] strings
    flag_t orth_flags
    flag_t dist_flags


cdef char* intern_and_encode(unicode string, size_t* length) except NULL

cdef int lexeme_get_int(LexemeC* lexeme, size_t i) except *

cdef float lexeme_get_float(LexemeC* lexeme, size_t i) except *

cdef unicode lexeme_get_string(LexemeC* lexeme, size_t i)

cdef bint lexeme_check_orth_flag(LexemeC* lexeme, size_t flag_id) except *

cdef bint lexeme_check_dist_flag(LexemeC* lexeme, size_t flag_id) except *

cdef dict lexeme_pack(LexemeC* lexeme)
cdef int lexeme_unpack(LexemeC* lexeme, dict p) except -1
