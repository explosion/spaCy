from .typedefs cimport hash_t, utf8_t, flag_t, id_t
from cymem.cymem cimport Pool


cdef struct LexemeC:
    size_t i
    size_t length
    double prob
    size_t cluster

    char* string
    
    char** views
    flag_t flags


cdef LexemeC* lexeme_init(Pool mem, size_t i, unicode string, double prob, size_t cluster,
                     list views, set flags)

cdef bint lexeme_check_flag(LexemeC* lexeme, size_t flag_id)
cdef unicode lexeme_string_view(LexemeC* lexeme, size_t view_id)


cdef dict lexeme_pack(LexemeC* lexeme)
cdef int lexeme_unpack(LexemeC* lexeme, dict p) except -1
