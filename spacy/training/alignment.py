from typing import List
import numpy
from thinc.types import Ragged
from dataclasses import dataclass

from .align import get_alignments


@dataclass
class Alignment:
    x2y: Ragged
    y2x: Ragged

    @classmethod
    def from_indices(cls, x2y: List[List[int]], y2x: List[List[int]]) -> "Alignment":
        x2y = _make_ragged(x2y)
        y2x = _make_ragged(y2x)
        return Alignment(x2y=x2y, y2x=y2x)

    @classmethod
    def from_strings(cls, A: List[str], B: List[str]) -> "Alignment":
        x2y, y2x = get_alignments(A, B)
        return Alignment.from_indices(x2y=x2y, y2x=y2x)


def _make_ragged(indices):
    lengths = numpy.array([len(x) for x in indices], dtype="i")
    flat = []
    for x in indices:
        flat.extend(x)
    return Ragged(numpy.array(flat, dtype="i"), lengths)
