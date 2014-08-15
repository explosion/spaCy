cpdef bytes to_bytes(unicode string)

cpdef unicode from_bytes(bytes string)

cpdef unicode substr(unicode string, int start, int end, size_t length)

cdef bint is_whitespace(Py_UNICODE c)
