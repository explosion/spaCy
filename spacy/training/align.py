from typing import List, Tuple
import numpy
from itertools import chain, islice
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


def get_alignments(A: List[str], B: List[str]) -> Tuple[List[List[int]], List[List[int]]]:
    """Calculate alignment tables between two tokenizations.

    tokens_a (List[str]): The first tokenization.
    tokens_b (List[str]): The second tokenization.
    RETURNS: (tuple): A tuple consisting of the following information:
      * a2b (List[List[int]): Mapping of indices in `tokens_a` to indices in
        `tokens_b`. For instance, if `a2b[4] == [6]`, that means that
        `tokens_a[4]` aligns to `tokens_b[6]`.
      * b2a (List[List[int]]): The same as `a2b`, but mapping the other
        direction.
    """
    if len(A) == 0 or len(B) == 0:
        if len(A) == 0 and len(B) == 0:
            return [], []
        else:
            raise ValueError(Errors.E949)
    # Remove whitespace from all non-whitespace tokens, replace all whitespace
    # tokens with a single space
    tokens_a = [x.replace(" ", "") if not x.isspace() else " " for x in A]
    tokens_b = [x.replace(" ", "") if not x.isspace() else " " for x in B]
    # Handle leading whitespace: replace whitespace tokens with empty strings
    # unless the whitespace is in both A and B
    if tokens_a[0].isspace() or tokens_b[0].isspace():
        tokens_a, tokens_b = _adjust_leading_whitespace(tokens_a, tokens_b)
    # Handle trailing whitespace: temporarily split off trailing whitespace
    # tokens and align them in the same way as leading whitespace
    if tokens_a[-1].isspace() or tokens_b[-1].isspace():
        tokens_a, tokens_b = _adjust_trailing_whitespace(tokens_a, tokens_b)
    # Check that the strings align, allowing only differences in capitalization
    if "".join(tokens_a).lower() != "".join(tokens_b).lower():
        raise ValueError(Errors.E949)
    # Create iterators for token indices per character position
    # Map the token indices per character range for each token
    token_by_char_a = chain(*((i,) * len(x) for i, x in enumerate(tokens_a)))
    token_by_char_b = chain(*((i,) * len(x) for i, x in enumerate(tokens_b)))
    a2b = [sorted(set(islice(token_by_char_b, len(t)))) for t in tokens_a]
    b2a = [sorted(set(islice(token_by_char_a, len(t)))) for t in tokens_b]
    return a2b, b2a


def _adjust_whitespace(tokens_a: List[str], str_a: str, str_b: str) -> None:
    """Replace whitespace tokens with empty strings at the beginning of the
    token list if the corresponding whitespace is not present in both strings.
    """
    for i in range(len(tokens_a)):
        if "".join(tokens_a[:i+1]).isspace():
            lead_len = sum(len(x) for x in tokens_a[:i+1])
            if str_a[:lead_len] != str_b[:lead_len]:
                tokens_a[i] = ''
        else:
            return


def _adjust_leading_whitespace(tokens_a: List[str], tokens_b: List[str]) -> Tuple[List[str], List[str]]:
    str_a = "".join(tokens_a)
    str_b = "".join(tokens_b)
    _adjust_whitespace(tokens_a, str_a, str_b)
    _adjust_whitespace(tokens_b, str_b, str_a)
    return tokens_a, tokens_b


def _adjust_trailing_whitespace(tokens_a: List[str], tokens_b: List[str]) -> Tuple[List[str], List[str]]:
    trailing_ws_start_a = _get_trailing_ws_start(tokens_a)
    trailing_ws_start_b = _get_trailing_ws_start(tokens_b)
    trailing_ws_a = tokens_a[trailing_ws_start_a:]
    trailing_ws_b = tokens_b[trailing_ws_start_b:]
    str_trailing_ws_a = "".join(trailing_ws_a)
    str_trailing_ws_b = "".join(trailing_ws_b)
    _adjust_whitespace(trailing_ws_a, str_trailing_ws_a, str_trailing_ws_b)
    _adjust_whitespace(trailing_ws_b, str_trailing_ws_b, str_trailing_ws_a)
    tokens_a = tokens_a[:trailing_ws_start_a] + trailing_ws_a
    tokens_b = tokens_b[:trailing_ws_start_b] + trailing_ws_b
    return tokens_a, tokens_b


def _get_trailing_ws_start(tokens: List[str]) -> int:
    """Return the index of the first trailing whitespace token."""
    trailing_ws_start = len(tokens)
    while trailing_ws_start > 0 and tokens[trailing_ws_start - 1].isspace():
        trailing_ws_start -= 1
    return trailing_ws_start
