from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool

import orth

OOV_DIST_FLAGS = 0


def get_lexeme_dict(size_t i, unicode string):
    ints = [None for _ in range(LexInt_N)]
    ints[<int>LexInt_i] = i
    ints[<int>LexInt_length] = len(string)
    ints[<int>LexInt_cluster] = 0
    ints[<int>LexInt_pos] = 0
    ints[<int>LexInt_supersense] = 0
    
    floats = [None for _ in range(LexFloat_N)]
    floats[<int>LexFloat_prob] = 0
    floats[<int>LexFloat_sentiment] = 0

    cdef size_t length
    strings = [None for _ in range(LexStr_N)]
    strings[<int>LexStr_key] = intern_and_encode(string, &length)
    strings[<int>LexStr_casefix] = strings[<int>LexStr_key]
    strings[<int>LexStr_shape] = intern_and_encode(orth.word_shape(string), &length)
    strings[<int>LexStr_unsparse] = strings[<int>LexStr_shape]
    strings[<int>LexStr_asciied] = intern_and_encode(orth.asciied(string), &length)

    orth_flags = get_orth_flags(string)
    dist_flags = OOV_DIST_FLAGS

    return {'ints': ints, 'floats': floats, 'strings': strings,
            'orth_flags': orth_flags, 'dist_flags': dist_flags}

def get_orth_flags(unicode string):
    return 0


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
        lex.ints[i] = lex_int
    cdef size_t _
    for i, lex_string in enumerate(p['strings']):
        lex.strings[i] = intern_and_encode(lex_string, &_)
    lex.orth_flags = p['orth_flags']
    lex.orth_flags = p['orth_flags']
