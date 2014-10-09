from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool


cdef LexemeC* lexeme_init(Pool mem, size_t i, unicode string, double prob,
                          size_t cluster, list views, set flags):
    cdef LexemeC* lexeme = <LexemeC*>mem.alloc(1, sizeof(LexemeC))
    lexeme.i = i
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


cdef dict lexeme_pack(LexemeC* lexeme):
    cdef dict packed = {}
    packed['i'] = lexeme.i
    packed['length'] = lexeme.length
    packed['prob'] = lexeme.prob
    packed['cluster'] = lexeme.cluster
    packed['string'] = lexeme.string.decode('utf8')
    packed['views'] = []
    cdef size_t i = 0
    while lexeme.views[i] != NULL:
        packed['views'].append(lexeme.views[i].decode('utf8'))
        i += 1
    packed['flags'] = lexeme.flags
    return packed


cdef int lexeme_unpack(LexemeC* lex, dict p) except -1:
    cdef size_t length
    lex.i = p['i']
    lex.length = p['length']
    lex.prob = p['prob']
    lex.cluster = p['cluster']
    lex.string = intern_and_encode(p['string'], &length)
    for i, view in enumerate(p['views']):
        lex.views[i] = intern_and_encode(view, &length)
    lex.flags = p['flags']
