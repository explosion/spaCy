from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool


cdef LexemeC* lexeme_init(Pool mem, unicode string, double prob, size_t cluster,
                     list views, set flags):
    cdef LexemeC* lexeme = <LexemeC*>mem.alloc(1, sizeof(LexemeC))
    lexeme.cluster = cluster
    lexeme.prob = prob
    lexeme.string = intern_and_encode(string, &lexeme.length)
    lexeme.views = <char**>mem.alloc(len(views), sizeof(char*))
    cdef size_t length = 0
    for i, string in enumerate(views):
        lexeme.views[i] = intern_and_encode(string, &length)

    for active_flag in flags:
        lexeme.flags |= (1 << active_flag)
    return lexeme


cdef char* intern_and_encode(unicode string, size_t* length):
    cdef bytes byte_string = string.encode('utf8')
    cdef bytes utf8_string = intern(byte_string)
    Py_INCREF(utf8_string)
    length[0] = len(utf8_string)
    return <char*>utf8_string


cdef bint lexeme_check_flag(LexemeC* lexeme, size_t flag_id):
    return lexeme.flags & (1 << flag_id)


cdef unicode lexeme_string_view(LexemeC* lexeme, size_t view_id):
    cdef bytes byte_string = lexeme.views[view_id]
    return byte_string.decode('utf8')
