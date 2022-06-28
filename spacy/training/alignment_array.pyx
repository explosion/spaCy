from typing import List
from ..errors import Errors
import numpy
from libc.stdint cimport int32_t


cdef class AlignmentArray:
    """AlignmentArray is similar to Thinc's Ragged with two simplfications:
    indexing returns numpy arrays and this type can only be used for CPU arrays.
    However, these changes make AlignmentArray more efficient for indexing in a
    tight loop."""

    __slots__ = []

    def __init__(self, alignment: List[List[int]]):
        cdef int data_len = 0
        cdef int outer_len
        cdef int idx

        self._starts_ends = numpy.zeros(len(alignment) + 1, dtype='int32')
        cdef int32_t* starts_ends_ptr = <int32_t*>self._starts_ends.data

        for idx, outer in enumerate(alignment):
            outer_len = len(outer)
            starts_ends_ptr[idx + 1] = starts_ends_ptr[idx] + outer_len
            data_len += outer_len

        self._lengths = None
        self._data = numpy.empty(data_len, dtype="int32")

        idx = 0
        cdef int32_t* data_ptr = <int32_t*>self._data.data

        for outer in alignment:
            for inner in outer:
                data_ptr[idx] = inner
                idx += 1

    def __getitem__(self, idx):
        starts = self._starts_ends[:-1]
        ends = self._starts_ends[1:]
        if isinstance(idx, int):
            start = starts[idx]
            end = ends[idx]
        elif isinstance(idx, slice):
            if not (idx.step is None or idx.step == 1):
                raise ValueError(Errors.E1027)
            start = starts[idx]
            if len(start) == 0:
                return self._data[0:0]
            start = start[0]
            end = ends[idx][-1]
        else:
            raise ValueError(Errors.E1028)

        return self._data[start:end]

    @property
    def data(self):
        return self._data

    @property
    def lengths(self):
        if self._lengths is None:
            self._lengths = self.ends - self.starts
        return self._lengths

    @property
    def ends(self):
        return self._starts_ends[1:]

    @property
    def starts(self):
        return self._starts_ends[:-1]
