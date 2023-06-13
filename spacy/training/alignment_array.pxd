cimport numpy as np
from libcpp.vector cimport vector


cdef class AlignmentArray:
    cdef np.ndarray _data
    cdef np.ndarray _lengths
    cdef np.ndarray _starts_ends
