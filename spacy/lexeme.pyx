from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool

import orth

OOV_DIST_FLAGS = 0


cpdef dict get_lexeme_dict(size_t i, unicode string):
    ints = [None for _ in range(LexInt_N)]
    ints[<int>LexInt_id] = i
    ints[<int>LexInt_length] = len(string)
    ints[<int>LexInt_cluster] = 0
    ints[<int>LexInt_pos] = 0
    ints[<int>LexInt_supersense] = 0
    
    floats = [None for _ in range(LexFloat_N)]
    floats[<int>LexFloat_prob] = 0
    floats[<int>LexFloat_sentiment] = 0

    strings = [None for _ in range(LexStr_N)]
    strings[<int>LexStr_orig] = string
    strings[<int>LexStr_norm] = strings[<int>LexStr_orig]
    strings[<int>LexStr_shape] = orth.word_shape(string)
    strings[<int>LexStr_unsparse] = strings[<int>LexStr_shape]
    strings[<int>LexStr_asciied] = orth.asciied(string)
    strings[<int>LexStr_pre] = string[0]
    strings[<int>LexStr_suff] = string[-3:]

    orth_flags = get_orth_flags(string)
    dist_flags = OOV_DIST_FLAGS

    return {'ints': ints, 'floats': floats, 'strings': strings,
            'orth_flags': orth_flags, 'dist_flags': dist_flags}

def get_orth_flags(unicode string):
    cdef flag_t flags = 0

    flags |= orth.is_ascii(string) << LexOrth_ascii
    flags |= orth.is_alpha(string) << LexOrth_alpha
    flags |= orth.is_digit(string) << LexOrth_digit
    flags |= orth.is_lower(string) << LexOrth_lower
    flags |= orth.is_punct(string) << LexOrth_punct
    flags |= orth.is_space(string) << LexOrth_space
    flags |= orth.is_title(string) << LexOrth_title
    flags |= orth.is_upper(string) << LexOrth_upper
    return flags


def get_dist_flags(unicode string):
    return 0


cdef char* intern_and_encode(unicode string, size_t* length) except NULL:
    cdef bytes byte_string = string.encode('utf8')
    cdef bytes utf8_string = intern(byte_string)
    Py_INCREF(utf8_string)
    length[0] = len(utf8_string)
    return <char*>utf8_string


cdef int lexeme_get_int(LexemeC* lexeme, size_t i) except *:
    return lexeme.ints[i]


cdef float lexeme_get_float(LexemeC* lexeme, size_t i) except *:
    return lexeme.floats[i]


cdef unicode lexeme_get_string(LexemeC* lexeme, size_t i):
    cdef bytes byte_string = lexeme.strings[i]
    return byte_string.decode('utf8')


cdef bint lexeme_check_orth_flag(LexemeC* lexeme, size_t flag_id) except *:
    return lexeme.orth_flags & (1 << flag_id)


cdef bint lexeme_check_dist_flag(LexemeC* lexeme, size_t flag_id) except *:
    return lexeme.dist_flags & (1 << flag_id)


cdef dict lexeme_pack(LexemeC* lex):
    cdef dict packed = {}
    packed['ints'] = [lex.ints[i] for i in range(LexInt_N)]
    packed['floats'] = [lex.floats[i] for i in range(LexFloat_N)]
    packed['strings'] = [lex.strings[i].decode('utf8') for i in range(LexStr_N)]
    packed['orth_flags'] = lex.orth_flags
    packed['dist_flags'] = lex.orth_flags
    return packed


cdef int lexeme_unpack(LexemeC* lex, dict p) except -1:
    cdef size_t i
    cdef int lex_int
    cdef float lex_float
    cdef unicode string
    for i, lex_int in enumerate(p['ints']):
        lex.ints[i] = lex_int
    for i, lex_float in enumerate(p['floats']):
        lex.floats[i] = lex_float
    cdef size_t _
    for i in range(LexStr_N):
        lex_string = p['strings'][i]
        lex.strings[i] = intern_and_encode(lex_string, &_)
    lex.orth_flags = p['orth_flags']
    lex.dist_flags = p['dist_flags']
