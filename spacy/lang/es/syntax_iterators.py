# coding: utf8
from __future__ import unicode_literals

from ...symbols import NOUN, PROPN, PRON, VERB, AUX
from ...errors import Errors


def noun_chunks(doclike):
    doc = doclike.doc

    if not doc.is_parsed:
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


def is_verb_token(token):
    return token.pos in [VERB, AUX]


def next_token(token):
    try:
        return token.nbor()
    except IndexError:
        return None


def noun_bounds(doc, root, np_left_deps, np_right_deps, stop_deps):
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
            if list(
                filter(
                    lambda t: is_verb_token(t) or t.dep in stop_deps,
                    doc[left_bound.i : right.i],
                )
            ):
                break
            else:
                right_bound = right
    return left_bound, right_bound


SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}
