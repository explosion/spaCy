from thinc.linear.avgtron cimport AveragedPerceptron
from thinc.extra.eg cimport Example
from thinc.structs cimport ExampleC
from thinc.linear.features cimport ConjunctionExtracter

from .structs cimport TokenC
from .vocab cimport Vocab


cdef class TaggerModel:
    cdef ConjunctionExtracter extracter
    cdef object model


cdef class Tagger:
    cdef readonly Vocab vocab
    cdef readonly TaggerModel model
    cdef public dict freqs
    cdef public object cfg
    cdef public object optimizer
