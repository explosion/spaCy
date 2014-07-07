cpdef unicode substr(unicode string, int start, int end, size_t length):
    if end >= length:
        end = -1
    if start >= length:
        start = 0
    if start <= 0 and end < 0:
        return string
    elif start < 0:
        start = 0
    elif end < 0:
        end = length
    return string[start:end]
  

cdef bint is_whitespace(Py_UNICODE c):
    # TODO: Support other unicode spaces
    # https://www.cs.tut.fi/~jkorpela/chars/spaces.html
    if c == u' ':
        return True
    elif c == u'\n':
        return True
    elif c == u'\t':
        return True
    else:
        return False
