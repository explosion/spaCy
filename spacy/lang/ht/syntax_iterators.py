from typing import Iterator, Tuple, Union

from ...errors import Errors
from ...symbols import NOUN, PRON, PROPN
from ...tokens import Doc, Span


def noun_chunks(doclike: Union[Doc, Span]) -> Iterator[Tuple[int, int, int]]:
    """
    Detect base noun phrases from a dependency parse for Haitian Creole.
    Works on both Doc and Span objects.
    """

    # Core nominal dependencies common in Haitian Creole
    labels = [
        "nsubj",
        "obj",
        "obl",
        "nmod",
        "appos",
        "ROOT",
    ]

    # Modifiers to optionally include in chunk (to the right)
    post_modifiers = ["compound", "flat", "flat:name", "fixed"]

    doc = doclike.doc
    if not doc.has_annotation("DEP"):
        raise ValueError(Errors.E029)

    np_deps = {doc.vocab.strings.add(label) for label in labels}
    np_mods = {doc.vocab.strings.add(mod) for mod in post_modifiers}
    conj_label = doc.vocab.strings.add("conj")
    np_label = doc.vocab.strings.add("NP")
    adp_pos = doc.vocab.strings.add("ADP")
    cc_pos = doc.vocab.strings.add("CCONJ")

    prev_end = -1
    for i, word in enumerate(doclike):
        if word.pos not in (NOUN, PROPN, PRON):
            continue
        if word.left_edge.i <= prev_end:
            continue

        if word.dep in np_deps:
            right_end = word
            # expand to include known modifiers to the right
            for child in word.rights:
                if child.dep in np_mods:
                    right_end = child.right_edge
                elif child.pos == NOUN:
                    right_end = child.right_edge

            left_index = word.left_edge.i
            # Skip prepositions at the start
            if word.left_edge.pos == adp_pos:
                left_index += 1

            prev_end = right_end.i
            yield left_index, right_end.i + 1, np_label

        elif word.dep == conj_label:
            head = word.head
            while head.dep == conj_label and head.head.i < head.i:
                head = head.head
            if head.dep in np_deps:
                left_index = word.left_edge.i
                if word.left_edge.pos == cc_pos:
                    left_index += 1
                prev_end = word.i
                yield left_index, word.i + 1, np_label


SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}
