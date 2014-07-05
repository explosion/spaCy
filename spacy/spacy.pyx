from __future__ import unicode_literals
from spacy.lexeme cimport Lexeme


cpdef vector[size_t] expand_chunk(size_t addr) except *:
    cdef vector[size_t] tokens = vector[size_t]()
    word = <Lexeme*>addr
    while word is not NULL:
        tokens.push_back(<size_t>word)
        word = word.tail
    return tokens


"""
cpdef vector[size_t] ids_from_text(unicode text) except *:
    cdef size_t length = len(text)
    cdef Py_UNICODE* characters = <Py_UNICODE*>text

    cdef size_t i
    cdef Py_UNICODE c

    cdef vector[size_t] tokens = vector[size_t]()
    cdef unicode current = u''
    cdef Lexeme* token
    cdef int alnum_end = -1
    cdef size_t alnum_start = 0
    cdef bint seen_alnum = False
    for i in range(length):
        c = characters[i]
        if is_whitespace(c):
            token = <Lexeme*>lookup(current)
            tokens.push_back(<size_t>token)
            clitic = 0
            while token.clitics[clitic]:
                tokens.push_back(token.clitics[clitic])
                clitic += 1
            current = u''
            alnum_start = 0
            alnum_end = -1
            seen_alnum = False
        else:
            if not seen_alnum and c.isalnum():
                alnum_start = i
                seen_alnum = True
            elif seen_alnum and alnum_end == -1 and not c.isalnum():
                alnum_end = i
            current += c
    if current:
        token = <Lexeme*>lookup(current)
        tokens.push_back(<size_t>token)
        clitic = 0
        while token.clitics[clitic]:
            tokens.push_back(token.clitics[clitic])
            clitic += 1
    return tokens
"""

#cdef vector[Tokens] group_by(Tokens tokens, LexAttr field) except *:
#    pass


cdef inline bint is_whitespace(Py_UNICODE c):
    # TODO: Support other unicode spaces
    # https://www.cs.tut.fi/~jkorpela/chars/spaces.html
    if c == u' ':
        return True
    elif c == u'\n':
        return True
    elif c == u'\t':
        return True
    else:
        return False
