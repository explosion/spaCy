from libc.stdio cimport fopen, fclose, fread, fwrite, FILE


cdef class CFile:
    def __init__(self, loc, mode, on_open_error=None):
        if isinstance(mode, unicode):
            mode_str = mode.encode('ascii')
        else:
            mode_str = mode
        if hasattr(loc, 'as_posix'):
            loc = loc.as_posix()
        cdef bytes bytes_loc = loc.encode('utf8') if type(loc) == unicode else loc
        self.fp = fopen(<char*>bytes_loc, mode_str)
        if self.fp == NULL:
            if on_open_error is not None:
                on_open_error()
            else:
                raise IOError("Could not open binary file %s" % bytes_loc)
        self.is_open = True

    def __dealloc__(self):
        if self.is_open:
            fclose(self.fp)

    def close(self):
        fclose(self.fp)
        self.is_open = False

    cdef int read_into(self, void* dest, size_t number, size_t elem_size) except -1:
        st = fread(dest, elem_size, number, self.fp)
        if st != number:
            raise IOError

    cdef int write_from(self, void* src, size_t number, size_t elem_size) except -1:
        st = fwrite(src, elem_size, number, self.fp)
        if st != number:
            raise IOError

    cdef void* alloc_read(self, Pool mem, size_t number, size_t elem_size) except *:
        cdef void* dest = mem.alloc(number, elem_size)
        self.read_into(dest, number, elem_size)
        return dest

    def write_unicode(self, unicode value):
        cdef bytes py_bytes = value.encode('utf8')
        cdef char* chars = <char*>py_bytes
        self.write(sizeof(char), len(py_bytes), chars)
