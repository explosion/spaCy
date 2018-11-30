# coding: utf8
from __future__ import unicode_literals

from ...symbols import NOUN, PROPN, PRON


def noun_chunks(obj):
    """
    Detect base noun phrases from a dependency parse. Works on both Doc and Span.
    """
    # this iterator extracts spans headed by NOUNs starting from the left-most
    # syntactic dependent until the NOUN itself for close apposition and
    # measurement construction, the span is sometimes extended to the right of
    # the NOUN. Example: "eine Tasse Tee" (a cup (of) tea) returns "eine Tasse Tee"
    # and not just "eine Tasse", same for "das Thema Familie".
    labels = [
        "sb",
        "oa",
        "da",
        "nk",
        "mo",
        "ag",
        "ROOT",
        "root",
        "cj",
        "pd",
        "og",
        "app",
    ]
    doc = obj.doc  # Ensure works on both Doc and Span.
    np_label = doc.vocab.strings.add("NP")
    np_deps = set(doc.vocab.strings.add(label) for label in labels)
    close_app = doc.vocab.strings.add("nk")

    rbracket = 0
    for i, word in enumerate(obj):
        if i < rbracket:
            continue
        if word.pos in (NOUN, PROPN, PRON) and word.dep in np_deps:
            rbracket = word.i + 1
            # try to extend the span to the right
            # to capture close apposition/measurement constructions
            for rdep in doc[word.i].rights:
                if rdep.pos in (NOUN, PROPN) and rdep.dep == close_app:
                    rbracket = rdep.i + 1
            yield word.left_edge.i, rbracket, np_label


SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}
