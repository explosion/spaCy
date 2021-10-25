from typing import Union, Iterator, Tuple

from ...symbols import NOUN, PROPN, PRON
from ...errors import Errors
from ...tokens import Doc, Span


def noun_chunks(doclike: Union[Doc, Span]) -> Iterator[Tuple[int, int, int]]:
    """
    Detect base noun phrases from a dependency parse. Works on both Doc and Span.
    """
    labels = [
        "nsubj",
        "nsubjpass",
        "obj",
        "nmod",
        "pcomp",
        "appos",
        "ROOT",
    ]
    post_modifiers = [
            "amod",
            "flat",
            "fixed",
            "compound"
    ]
    doc = doclike.doc  # Ensure works on both Doc and Span.
    if not doc.has_annotation("DEP"):
        raise ValueError(Errors.E029)
    np_deps = [doc.vocab.strings.add(label) for label in labels]
    np_modifs = [doc.vocab.strings.add(modifier) for modifier in post_modifiers]
    np_label = doc.vocab.strings.add("NP")
    prev_end = -1
    for i, word in enumerate(doclike):
        if word.pos not in (NOUN, PROPN, PRON):
            continue
        # Prevent nested chunks from being produced
        if word.left_edge.i <= prev_end:
            print(word, word.left_edge.i, prev_end, "edges")
            continue
        if word.dep in np_deps:
            print(word, word.left_edge.i, prev_end, "edges")
            right_childs = list(word.rights)
            right_child = right_childs[0] if right_childs else None
            right_end = right_child.right_edge if right_child and right_child.dep in np_modifs else word
            prev_end = right_end.i
            yield word.left_edge.i, right_end.i + 1, np_label




SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}

