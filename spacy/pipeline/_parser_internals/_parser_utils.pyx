# cython: infer_types=True

cdef inline int arg_max(const float* scores, const int n_classes) nogil:
    if n_classes == 2:
        return 0 if scores[0] > scores[1] else 1
    cdef int i
    cdef int best = 0
    cdef float mode = scores[0]
    for i in range(1, n_classes):
        if scores[i] > mode:
            mode = scores[i]
            best = i
    return best


cdef inline int arg_max_if_valid(const float* scores, const int* is_valid, int n) nogil:
    cdef int best = -1
    for i in range(n):
        if is_valid[i] >= 1:
            if best == -1 or scores[i] > scores[best]:
                best = i
    return best
