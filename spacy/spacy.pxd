from libcpp.vector cimport vector
from spacy.lexeme cimport Lexeme


cpdef vector[size_t] expand_chunk(size_t addr) except *
