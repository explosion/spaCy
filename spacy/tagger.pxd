from .structs cimport TokenC
from .vocab cimport Vocab
from ._ml cimport LinearModel
from thinc.structs cimport FeatureC
from thinc.typedefs cimport atom_t


cdef class TaggerModel(LinearModel):
    cdef int set_featuresC(self, FeatureC* features, atom_t* context,
            const TokenC* tokens, int i) nogil
 


cdef class Tagger:
    cdef readonly Vocab vocab
    cdef readonly TaggerModel model
    cdef public dict freqs
    cdef public object cfg
    cdef public object optimizer
