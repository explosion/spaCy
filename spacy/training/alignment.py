from typing import List
from dataclasses import dataclass

from .align import get_alignments
from .alignment_array import AlignmentArray


@dataclass
class Alignment:
    x2y: AlignmentArray
    y2x: AlignmentArray

    @classmethod
    def from_indices(cls, x2y: List[List[int]], y2x: List[List[int]]) -> "Alignment":
        x2y = AlignmentArray(x2y)
        y2x = AlignmentArray(y2x)
        return Alignment(x2y=x2y, y2x=y2x)

    @classmethod
    def from_strings(cls, A: List[str], B: List[str]) -> "Alignment":
        x2y, y2x = get_alignments(A, B)
        return Alignment.from_indices(x2y=x2y, y2x=y2x)
