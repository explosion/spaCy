from typing import Union, Iterator

from ...symbols import NOUN, PROPN, PRON
from ...errors import Errors
from ...tokens import Doc, Span


def noun_chunks(doclike: Union[Doc, Span]) -> Iterator[Span]:
    """Detect base noun phrases from a dependency parse. Works on Doc and Span."""
    # fmt: off
    labels = ["nsubj", "dobj", "nsubjpass", "pcomp", "pobj", "dative", "appos", "attr", "ROOT"]
    # fmt: on
    doc = doclike.doc  # Ensure works on both Doc and Span.
    if not doc.has_annotation("DEP"):
        raise ValueError(Errors.E029)
    np_deps = [doc.vocab.strings.add(label) for label in labels]
    conj = doc.vocab.strings.add("conj")
    np_label = doc.vocab.strings.add("NP")
    prev_end = -1
    for i, word in enumerate(doclike):
        if word.pos not in (NOUN, PROPN, PRON):
            continue
        # Prevent nested chunks from being produced
        if word.left_edge.i <= prev_end:
            continue
        if word.dep in np_deps:
            prev_end = word.i
            yield word.left_edge.i, word.i + 1, np_label
        elif word.dep == conj:
            head = word.head
            while head.dep == conj and head.head.i < head.i:
                head = head.head
            # If the head is an NP, and we're coordinated to it, we're an NP
            if head.dep in np_deps:
                prev_end = word.i
                yield word.left_edge.i, word.i + 1, np_label


SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}
