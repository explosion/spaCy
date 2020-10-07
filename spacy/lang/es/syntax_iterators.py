from typing import Union, Iterator, Optional, List, Tuple

from ...symbols import NOUN, PROPN, PRON, VERB, AUX
from ...errors import Errors
from ...tokens import Doc, Span, Token


def noun_chunks(doclike: Union[Doc, Span]) -> Iterator[Span]:
    """Detect base noun phrases from a dependency parse. Works on Doc and Span."""
    doc = doclike.doc
    if not doc.has_annotation("DEP"):
        raise ValueError(Errors.E029)
    if not len(doc):
        return
    np_label = doc.vocab.strings.add("NP")
    left_labels = ["det", "fixed", "neg"]  # ['nunmod', 'det', 'appos', 'fixed']
    right_labels = ["flat", "fixed", "compound", "neg"]
    stop_labels = ["punct"]
    np_left_deps = [doc.vocab.strings.add(label) for label in left_labels]
    np_right_deps = [doc.vocab.strings.add(label) for label in right_labels]
    stop_deps = [doc.vocab.strings.add(label) for label in stop_labels]
    for token in doclike:
        if token.pos in [PROPN, NOUN, PRON]:
            left, right = noun_bounds(
                doc, token, np_left_deps, np_right_deps, stop_deps
            )
            yield left.i, right.i + 1, np_label
            token = right
        token = next_token(token)


def is_verb_token(token: Token) -> bool:
    return token.pos in [VERB, AUX]


def next_token(token: Token) -> Optional[Token]:
    try:
        return token.nbor()
    except IndexError:
        return None


def noun_bounds(
    doc: Doc,
    root: Token,
    np_left_deps: List[str],
    np_right_deps: List[str],
    stop_deps: List[str],
) -> Tuple[Token, Token]:
    left_bound = root
    for token in reversed(list(root.lefts)):
        if token.dep in np_left_deps:
            left_bound = token
    right_bound = root
    for token in root.rights:
        if token.dep in np_right_deps:
            left, right = noun_bounds(
                doc, token, np_left_deps, np_right_deps, stop_deps
            )
            filter_func = lambda t: is_verb_token(t) or t.dep in stop_deps
            if list(filter(filter_func, doc[left_bound.i : right.i])):
                break
            else:
                right_bound = right
    return left_bound, right_bound


SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}
