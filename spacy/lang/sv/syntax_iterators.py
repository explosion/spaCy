# coding: utf8
from __future__ import unicode_literals

from ...symbols import NOUN, PROPN, PRON
from ...errors import Errors


def noun_chunks(doclike):
    """
    Detect base noun phrases from a dependency parse. Works on both Doc and Span.
    """
    labels = [
        "nsubj",
        "nsubj:pass",
        "dobj",
        "obj",
        "iobj",
        "ROOT",
        "appos",
        "nmod",
        "nmod:poss",
    ]
    doc = doclike.doc  # Ensure works on both Doc and Span.

    if not doc.is_parsed:
        raise ValueError(Errors.E029)

    np_deps = [doc.vocab.strings[label] for label in labels]
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
            prev_end = word.right_edge.i
            yield word.left_edge.i, word.right_edge.i + 1, np_label
        elif word.dep == conj:
            head = word.head
            while head.dep == conj and head.head.i < head.i:
                head = head.head
            # If the head is an NP, and we're coordinated to it, we're an NP
            if head.dep in np_deps:
                prev_end = word.right_edge.i
                yield word.left_edge.i, word.right_edge.i + 1, np_label


SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}
