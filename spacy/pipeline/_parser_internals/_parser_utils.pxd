cdef int arg_max(const float* scores, const int n_classes) nogil
cdef int arg_max_if_valid(const float* scores, const int* is_valid, int n) nogil
