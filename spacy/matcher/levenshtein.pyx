# cython: binding=True, infer_types=True, language_level=3
from cpython.object cimport PyObject
from libc.stdint cimport int64_t

from typing import Optional

from ..util import registry


cdef extern from "polyleven.c":
    int64_t polyleven(PyObject *o1, PyObject *o2, int64_t k)


cpdef int64_t levenshtein(a: str, b: str, k: Optional[int] = None):
    if k is None:
        k = -1
    return polyleven(<PyObject*>a, <PyObject*>b, k)


cpdef bint levenshtein_compare(input_text: str, pattern_text: str, fuzzy: int = -1):
    if fuzzy >= 0:
        max_edits = fuzzy
    else:
        # allow at least two edits (to allow at least one transposition) and up
        # to 30% of the pattern string length
        max_edits = max(2, round(0.3 * len(pattern_text)))
    return levenshtein(input_text, pattern_text, max_edits) <= max_edits


def make_levenshtein_compare():
    return levenshtein_compare
