from typing import List
import numpy
from itertools import chain
from thinc.types import Ragged
from dataclasses import dataclass

from ..errors import Errors


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


def get_alignments(A: List[str], B: List[str]) -> (List[List[int]], List[List[int]]):
    """Calculate alignment tables between two tokenizations.

    tokens_a (List[str]): The first tokenization.
    tokens_b (List[str]): The second tokenization.
    RETURNS: (tuple): A 5-tuple consisting of the following information:
      * a2b (List[List[int]): Mapping of indices in `tokens_a` to indices in
        `tokens_b`. For instance, if `a2b[4] == [6]`, that means that
        `tokens_a[4]` aligns to `tokens_b[6]`.
      * b2a (List[List[int]]): The same as `a2b`, but mapping the other
        direction.
    """
    # Remove whitespace from all non-whitespace tokens
    tokens_a = [x.replace(" ", "") if not x.isspace() else x for x in A]
    tokens_b = [x.replace(" ", "") if not x.isspace() else x for x in B]
    # Remove leading/trailing whitespace tokens unless the whitespace is in
    # both A and B
    str_a = "".join(tokens_a)
    str_b = "".join(tokens_b)
    # Handle leading whitespace
    for i in range(len(tokens_a)):
        if "".join(tokens_a[:i+1]).isspace():
            lead_len = sum([len(x) for x in tokens_a[:i+1]])
            if str_a[:lead_len] != str_b[:lead_len]:
                tokens_a[i] = ''
        else:
            break
    for i in range(len(tokens_b)):
        if "".join(tokens_b[:i+1]).isspace():
            lead_len = sum([len(x) for x in tokens_b[:i+1]])
            if str_a[:lead_len] != str_b[:lead_len]:
                tokens_b[i] = ''
        else:
            break
    # Handle trailing whitespace
    # (Note that iterating through the tokens in reverse as below leads to a
    # slightly different alignment than with pytokenizations for the trailing
    # whitespace characters.)
    for i in range(len(tokens_a)-1, -1, -1):
        if "".join(tokens_a[i:]).isspace():
            trail_len = sum([len(x) for x in tokens_a[i:]])
            if str_a[-trail_len:] != str_b[-trail_len:]:
                tokens_a[i] = ''
        else:
            break
    for i in range(len(tokens_b)-1, -1, -1):
        if "".join(tokens_b[i:]).isspace():
            trail_len = sum([len(x) for x in tokens_b[i:]])
            if str_a[-trail_len:] != str_b[-trail_len:]:
                tokens_b[i] = ''
        else:
            break
    # Check that the tokens align, allowing only differences in capitalization
    if "".join(tokens_a).lower() != "".join(tokens_b).lower():
        raise ValueError(Errors.E949)
    a2b = [set() for i in range(len(tokens_a))]
    b2a = [set() for i in range(len(tokens_b))]
    # Create iterators for token indices per character position
    a_i = chain(*[[i] * len(x) for i, x in enumerate(tokens_a)])
    b_i = chain(*[[i] * len(x) for i, x in enumerate(tokens_b)])
    # Map the token indices per character range for each token
    for i, token_a in enumerate(tokens_a):
        for j in range(len(token_a)):
            a2b[i].add(next(b_i))
    for i, token_b in enumerate(tokens_b):
        for j in range(len(token_b)):
            b2a[i].add(next(a_i))
    # Convert the token index sets to sorted lists
    a2b = [sorted(x) for x in a2b]
    b2a = [sorted(x) for x in b2a]
    return a2b, b2a
