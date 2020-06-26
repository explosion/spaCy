import numpy
from ..errors import Errors, AlignmentError


cdef class Alignment:
    def __init__(self, spacy_words, gold_words):
        # Do many-to-one alignment for misaligned tokens.
        # If we over-segment, we'll have one gold word that covers a sequence
        # of predicted words
        # If we under-segment, we'll have one predicted word that covers a
        # sequence of gold words.
        # If we "mis-segment", we'll have a sequence of predicted words covering
        # a sequence of gold words. That's many-to-many -- we don't do that
        # except for NER spans where the start and end can be aligned.
        cost, i2j, j2i, i2j_multi, j2i_multi = align(spacy_words, gold_words)
        self.cost = cost
        self.i2j = i2j
        self.j2i = j2i
        self.i2j_multi = i2j_multi
        self.j2i_multi = j2i_multi
        self.cand_to_gold = [(j if j >= 0 else None) for j in i2j]
        self.gold_to_cand = [(i if i >= 0 else None) for i in j2i]


def align(tokens_a, tokens_b):
    """Calculate alignment tables between two tokenizations.

    tokens_a (List[str]): The candidate tokenization.
    tokens_b (List[str]): The reference tokenization.
    RETURNS: (tuple): A 5-tuple consisting of the following information:
      * cost (int): The number of misaligned tokens.
      * a2b (List[int]): Mapping of indices in `tokens_a` to indices in `tokens_b`.
        For instance, if `a2b[4] == 6`, that means that `tokens_a[4]` aligns
        to `tokens_b[6]`. If there's no one-to-one alignment for a token,
        it has the value -1.
      * b2a (List[int]): The same as `a2b`, but mapping the other direction.
      * a2b_multi (Dict[int, int]): A dictionary mapping indices in `tokens_a`
        to indices in `tokens_b`, where multiple tokens of `tokens_a` align to
        the same token of `tokens_b`.
      * b2a_multi (Dict[int, int]): As with `a2b_multi`, but mapping the other
            direction.
    """
    tokens_a = _normalize_for_alignment(tokens_a)
    tokens_b = _normalize_for_alignment(tokens_b)
    cost = 0
    a2b = numpy.empty(len(tokens_a), dtype="i")
    b2a = numpy.empty(len(tokens_b), dtype="i")
    a2b.fill(-1)
    b2a.fill(-1)
    a2b_multi = {}
    b2a_multi = {}
    i = 0
    j = 0
    offset_a = 0
    offset_b = 0
    while i < len(tokens_a) and j < len(tokens_b):
        a = tokens_a[i][offset_a:]
        b = tokens_b[j][offset_b:]
        if a == b:
            if offset_a == offset_b == 0:
                a2b[i] = j
                b2a[j] = i
            elif offset_a == 0:
                cost += 2
                a2b_multi[i] = j
            elif offset_b == 0:
                cost += 2
                b2a_multi[j] = i
            offset_a = offset_b = 0
            i += 1
            j += 1
        elif a == "":
            assert offset_a == 0
            cost += 1
            i += 1
        elif b == "":
            assert offset_b == 0
            cost += 1
            j += 1
        elif b.startswith(a):
            cost += 1
            if offset_a == 0:
                a2b_multi[i] = j
            i += 1
            offset_a = 0
            offset_b += len(a)
        elif a.startswith(b):
            cost += 1
            if offset_b == 0:
                b2a_multi[j] = i
            j += 1
            offset_b = 0
            offset_a += len(b)
        else:
            assert "".join(tokens_a) != "".join(tokens_b)
            raise AlignmentError(Errors.E186.format(tok_a=tokens_a, tok_b=tokens_b))
    return cost, a2b, b2a, a2b_multi, b2a_multi


def _normalize_for_alignment(tokens):
    return [w.replace(" ", "").lower() for w in tokens]
