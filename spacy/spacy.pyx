from __future__ import unicode_literals
from spacy.lexeme cimport Lexeme


cpdef vector[size_t] expand_chunk(size_t addr) except *:
    cdef vector[size_t] tokens = vector[size_t]()
    word = <Lexeme*>addr
    while word is not NULL:
        tokens.push_back(<size_t>word)
        word = word.tail
    return tokens


