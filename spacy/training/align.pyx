import re
from itertools import chain
from typing import List, Tuple

from ..errors import Errors


def get_alignments(A: List[str], B: List[str]) -> Tuple[List[List[int]], List[List[int]]]:
    # Create character-to-token mappings
    char_to_token_a = tuple(chain(*((i,) * len(x.lower()) for i, x in enumerate(A))))
    char_to_token_b = tuple(chain(*((i,) * len(x.lower()) for i, x in enumerate(B))))
    str_a = "".join(A).lower()
    str_b = "".join(B).lower()
    cdef int len_str_a = len(str_a)
    cdef int len_str_b = len(str_b)
    # Check that the two texts only differ in whitespace and capitalization
    if re.sub(r"\s+", "", str_a) != re.sub(r"\s+", "", str_b) or \
            len_str_a != len(char_to_token_a) or \
            len_str_b != len(char_to_token_b):
        raise ValueError(Errors.E949.format(x=str(A[:10]), y=str(B[:10])))
    cdef int char_idx_a = 0
    cdef int char_idx_b = 0
    cdef int token_idx_a = 0
    cdef int token_idx_b = 0
    cdef int prev_token_idx_a = -1
    cdef int prev_token_idx_b = -1
    a2b = []
    b2a = []
    while char_idx_a < len_str_a and char_idx_b < len_str_b:
        # Find the current token position from the character position
        token_idx_a = char_to_token_a[char_idx_a]
        token_idx_b = char_to_token_b[char_idx_b]
        # Add a set for the next token if a token boundary has been crossed
        if prev_token_idx_a != token_idx_a:
            a2b.append(set())
        if prev_token_idx_b != token_idx_b:
            b2a.append(set())
        # Process the alignment at the current position
        if A[token_idx_a] == B[token_idx_b] and \
                (char_idx_a == 0 or \
                    char_to_token_a[char_idx_a - 1] < token_idx_a) and \
                (char_idx_b == 0 or \
                    char_to_token_b[char_idx_b - 1] < token_idx_b):
            # Current tokens are identical and both character offsets are the
            # start of a token (either at the beginning of the document or the
            # previous character belongs to a different token)
            a2b[-1].add(token_idx_b)
            b2a[-1].add(token_idx_a)
            char_idx_a += len(A[token_idx_a])
            char_idx_b += len(B[token_idx_b])
        elif str_a[char_idx_a] == str_b[char_idx_b]:
            # Current chars are identical
            a2b[-1].add(token_idx_b)
            b2a[-1].add(token_idx_a)
            char_idx_a += 1
            char_idx_b += 1
        elif str_a[char_idx_a].isspace():
            # Skip unaligned whitespace char in A
            char_idx_a += 1
        elif str_b[char_idx_b].isspace():
            # Skip unaligned whitespace char in B
            char_idx_b += 1
        else:
            # This should never happen
            raise ValueError(Errors.E949.format(x=str(A[:10]), y=str(B[:10])))
        prev_token_idx_a = token_idx_a
        prev_token_idx_b = token_idx_b
    # Process unaligned trailing whitespace
    a2b.extend([set()] * len(set(char_to_token_a[char_idx_a:])))
    b2a.extend([set()] * len(set(char_to_token_b[char_idx_b:])))
    # Return values as sorted lists per token position
    return [sorted(x) for x in a2b], [sorted(x) for x in b2a]
