from ..tagger cimport Tagger
from ..morphology cimport Morphologizer


cdef class EnPosTagger(Tagger):
    cdef Morphologizer morphologizer
