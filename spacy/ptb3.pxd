from spacy.lang cimport Language


cdef class PennTreebank3(Language):
    cdef list _split(self, unicode split)
