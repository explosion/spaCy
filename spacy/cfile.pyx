# coding: utf8
from __future__ import unicode_literals

from libc.stdio cimport fopen, fclose, fread, fwrite
from libc.string cimport memcpy


cdef class CFile:
    def __init__(self, loc, mode, on_open_error=None):
        if isinstance(mode, unicode):
            mode_str = mode.encode('ascii')
        else:
            mode_str = mode
        if hasattr(loc, 'as_posix'):
            loc = loc.as_posix()
        self.mem = Pool()
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


cdef class StringCFile:
    def __init__(self, bytes data, mode, on_open_error=None):
        self.mem = Pool()
        self.is_open = 1 if 'w' in mode else 0
        self._capacity = max(len(data), 8)
        self.size = len(data)
        self.i = 0
        self.data = <unsigned char*>self.mem.alloc(1, self._capacity)
        for i in range(len(data)):
            self.data[i] = data[i]

    def __dealloc__(self):
        # Important to override this -- or
        # we try to close a non-existant file pointer!
        pass

    def close(self):
        self.is_open = False

    def string_data(self):
        cdef bytes byte_string = b'\0' * (self.size)
        bytes_ptr = <char*>byte_string
        for i in range(self.size):
            bytes_ptr[i] = self.data[i]
        print(byte_string)
        return byte_string

    cdef int read_into(self, void* dest, size_t number, size_t elem_size) except -1:
        if self.i+(number * elem_size) < self.size:
            memcpy(dest, &self.data[self.i], elem_size * number)
            self.i += elem_size * number

    cdef int write_from(self, void* src, size_t elem_size, size_t number) except -1:
        write_size = number * elem_size
        if (self.size + write_size) >= self._capacity:
            self._capacity = (self.size + write_size) * 2
            self.data = <unsigned char*>self.mem.realloc(self.data, self._capacity)
        memcpy(&self.data[self.size], src, write_size)
        self.size += write_size

    cdef void* alloc_read(self, Pool mem, size_t number, size_t elem_size) except *:
        cdef void* dest = mem.alloc(number, elem_size)
        self.read_into(dest, number, elem_size)
        return dest

    def write_unicode(self, unicode value):
        cdef bytes py_bytes = value.encode('utf8')
        cdef char* chars = <char*>py_bytes
        self.write(sizeof(char), len(py_bytes), chars)
