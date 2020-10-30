# coding: utf8
from __future__ import unicode_literals

from ...symbols import NOUN, PROPN, PRON, VERB, AUX
from ...errors import Errors


def noun_chunks(doclike):
    def is_verb_token(tok):
        return tok.pos in [VERB, AUX]

    def next_token(tok):
        try:
            return tok.nbor()
        except IndexError:
            return None

    def get_left_bound(doc, root):
        left_bound = root
        for tok in reversed(list(root.lefts)):
            if tok.dep in np_left_deps:
                left_bound = tok
        return left_bound

    def get_right_bound(doc, root):
        right_bound = root
        for tok in root.rights:
            if tok.dep in np_right_deps:
                right = get_right_bound(doc, tok)
                if list(
                    filter(
                        lambda t: is_verb_token(t) or t.dep in stop_deps,
                        doc[root.i : right.i],
                    )
                ):
                    break
                else:
                    right_bound = right
        return right_bound

    def get_bounds(doc, root):
        return get_left_bound(doc, root), get_right_bound(doc, root)

    doc = doclike.doc

    if not doc.is_parsed:
        raise ValueError(Errors.E029)

    if not len(doc):
        return

    left_labels = [
        "det",
        "fixed",
        "nmod:poss",
        "amod",
        "flat",
        "goeswith",
        "nummod",
        "appos",
    ]
    right_labels = ["fixed", "nmod:poss", "amod", "flat", "goeswith", "nummod", "appos"]
    stop_labels = ["punct"]

    np_label = doc.vocab.strings.add("NP")
    np_left_deps = [doc.vocab.strings.add(label) for label in left_labels]
    np_right_deps = [doc.vocab.strings.add(label) for label in right_labels]
    stop_deps = [doc.vocab.strings.add(label) for label in stop_labels]

    chunks = []
    for token in doclike:
        if token.pos in [PROPN, NOUN, PRON]:
            left, right = get_bounds(doc, token)
            chunks.append((left.i, right.i + 1, np_label))
            token = right

    is_chunk = [True for _ in chunks]
    # remove nested chunks
    for i, i_chunk in enumerate(chunks[:-1]):
        i_left, i_right, _ = i_chunk
        for j, j_chunk in enumerate(chunks[i+1:], start=i+1):
            j_left, j_right, _ = j_chunk
            if j_left <= i_left < i_right <= j_right:
                is_chunk[i] = False
            if i_left <= j_left < j_right <= i_right:
                is_chunk[j] = False

    for chk, ischk in zip(chunks, is_chunk):
        if is_chunk:
            yield chk


SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}
