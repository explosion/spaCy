from typing import Union, Iterator

from ...symbols import NOUN, PROPN, PRON
from ...errors import Errors
from ...tokens import Doc, Span


def noun_chunks(doclike: Union[Doc, Span]) -> Iterator[Span]:
    """Detect base noun phrases from a dependency parse. Works on Doc and Span."""
    # fmt: off
    labels = ["nsubj", "nsubj:pass", "dobj", "obj", "iobj", "ROOT", "appos", "nmod", "nmod:poss"]
    # fmt: on
    doc = doclike.doc  # type: ignore[union-attr]    # Ensure works on both Doc and Span.
    if not doc.has_annotation("DEP"):
        raise ValueError(Errors.E029)
    np_deps = [doc.vocab.strings[label] for label in labels]  # type: ignore[union-attr]
    conj = doc.vocab.strings.add("conj")  # type: ignore[union-attr]
    np_label = doc.vocab.strings.add("NP")  # type: ignore[union-attr]
    prev_end = -1
    for i, word in enumerate(doclike):
        if word.pos not in (NOUN, PROPN, PRON):
            continue
        # Prevent nested chunks from being produced
        if word.left_edge.i <= prev_end:
            continue
        if word.dep in np_deps:
            prev_end = word.right_edge.i
            yield word.left_edge.i, word.right_edge.i + 1, np_label  # type: ignore[misc]
        elif word.dep == conj:
            head = word.head
            while head.dep == conj and head.head.i < head.i:
                head = head.head
            # If the head is an NP, and we're coordinated to it, we're an NP
            if head.dep in np_deps:
                prev_end = word.right_edge.i
                yield word.left_edge.i, word.right_edge.i + 1, np_label  # type: ignore[misc]


SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}
