
from spacy.tokens.doc cimport Doc

cdef dict CHUNKERS

cdef class DocIterator:
    cdef Doc _doc

cdef class EnglishNounChunks(DocIterator):
    cdef int i
    cdef int _np_label
    cdef set _np_deps
    cdef int _conjunct

cdef class GermanNounChunks(DocIterator):
    cdef int i
    cdef int _np_label
    cdef set _np_deps
    cdef int _close_app
