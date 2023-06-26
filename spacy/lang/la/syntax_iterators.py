from typing import Iterator, Tuple, Union

from ...errors import Errors
from ...symbols import AUX, NOUN, PRON, PROPN, VERB
from ...tokens import Doc, Span

# NB: Modified from da on suggestion from https://github.com/explosion/spaCy/issues/7457#issuecomment-800349751 [PJB]


def noun_chunks(doclike: Union[Doc, Span]) -> Iterator[Tuple[int, int, int]]:
    def is_verb_token(tok):
        return tok.pos in [VERB, AUX]

    def get_left_bound(root):
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
        return get_left_bound(root), get_right_bound(doc, root)

    doc = doclike.doc  # Ensure works on both Doc and Span.

    if not doc.has_annotation("DEP"):
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
    right_labels = [
        "fixed",
        "nmod:poss",
        "amod",
        "flat",
        "goeswith",
        "nummod",
        "appos",
        "nmod",
        "det",
    ]
    stop_labels = ["punct"]

    np_label = doc.vocab.strings.add("NP")
    np_left_deps = [doc.vocab.strings.add(label) for label in left_labels]
    np_right_deps = [doc.vocab.strings.add(label) for label in right_labels]
    stop_deps = [doc.vocab.strings.add(label) for label in stop_labels]

    prev_right = -1
    for token in doclike:
        if token.pos in [PROPN, NOUN, PRON]:
            left, right = get_bounds(doc, token)
            if left.i <= prev_right:
                continue
            yield left.i, right.i + 1, np_label
            prev_right = right.i


SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}
