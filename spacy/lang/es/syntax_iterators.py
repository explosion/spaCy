# coding: utf8
from __future__ import unicode_literals

from ...symbols import NOUN, PROPN, PRON, VERB, AUX


def noun_chunks(obj):
    doc = obj.doc
    np_label = doc.vocab.strings.add('NP')
    left_labels = ['det', 'fixed', 'neg'] # ['nunmod', 'det', 'appos', 'fixed']
    right_labels = ['flat', 'fixed', 'compound', 'neg']
    stop_labels = ['punct']
    np_left_deps = [doc.vocab.strings[label] for label in left_labels]
    np_right_deps = [doc.vocab.strings[label] for label in right_labels]
    stop_deps = [doc.vocab.strings[label] for label in stop_labels]

    def noun_bounds(root):
        left_bound = root
        for token in reversed(list(root.lefts)):
            if token.dep in np_left_deps:
                left_bound = token
        right_bound = root
        for token in root.rights:
            if (token.dep in np_right_deps):
                left, right = noun_bounds(token)
                if list(filter(lambda t: is_verb_token(t) or t.dep in stop_deps,
                            doc[left_bound.i: right.i])):
                    break
                else:
                    right_bound = right
        return left_bound, right_bound

    token = doc[0]
    while token and token.i < len(doc):
        if token.pos in [PROPN, NOUN, PRON]:
            left, right = noun_bounds(token)
            yield left.i, right.i+1, np_label
            token = right
        token = next_token(token)


def is_verb_token(token):
    return token.pos in [VERB, AUX]


def next_token(token):
    try:
        return token.nbor()
    except:
        return None


SYNTAX_ITERATORS = {
    'noun_chunks': noun_chunks
}
