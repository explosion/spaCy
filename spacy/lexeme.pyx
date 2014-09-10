from libc.stdlib cimport calloc, free


cdef LexemeC* lexeme_init(unicode string, double prob, size_t cluster,
                     list views, set flags):
    cdef LexemeC* lexeme = <LexemeC*>calloc(1, sizeof(LexemeC))
    lexeme.cluster = cluster
    lexeme.prob = prob
    lexeme.length = len(string)
    lexeme.string = intern_and_encode(string)

    lexeme.views = <char**>calloc(len(views), sizeof(char*))
    for i, string in enumerate(views):
        lexeme.views[i] = intern_and_encode(string)

    for active_flag in flags:
        lexeme.flags |= (1 << active_flag)
    return lexeme


cdef int lexeme_free(LexemeC* lexeme) except -1:
    free(lexeme.views)
    free(lexeme)
    

cdef set _strings = set()
cdef char* intern_and_encode(unicode string):
    global _strings
    cdef bytes utf8_string = intern(string.encode('utf8'))
    _strings.add(utf8_string)
    return <char*>utf8_string


cdef bint lexeme_check_flag(LexemeC* lexeme, size_t flag_id):
    return lexeme.flags & (1 << flag_id)


cdef unicode lexeme_string_view(LexemeC* lexeme, size_t view_id):
    cdef bytes byte_string = lexeme.views[view_id]
    return byte_string.decode('utf8')
