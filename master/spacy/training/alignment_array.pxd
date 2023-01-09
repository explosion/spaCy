from libcpp.vector cimport vector
cimport numpy as np

cdef class AlignmentArray:
    cdef np.ndarray _data
    cdef np.ndarray _lengths
    cdef np.ndarray _starts_ends
