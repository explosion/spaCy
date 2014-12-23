from ..tagger cimport Tagger
from ..morphology cimport Morphologizer
from ..strings cimport StringStore


cdef class EnPosTagger(Tagger):
    cdef readonly StringStore strings
    cdef readonly StringStore tags
    cdef readonly Morphologizer morphologizer
