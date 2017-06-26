# coding: utf8
from __future__ import unicode_literals

from ...symbols import NOUN, PROPN, PRON


def noun_chunks(obj):
    """
    Detect base noun phrases from a dependency parse. Works on both Doc and Span.
    """
    labels = ['nsubj', 'nsubj:pass', 'obj', 'iobj', 'ROOT', 'appos', 'nmod', 'nmod:poss']
    doc = obj.doc  # Ensure works on both Doc and Span.
    np_deps = [doc.vocab.strings[label] for label in labels]
    conj = doc.vocab.strings.add('conj')
    np_label = doc.vocab.strings.add('NP')
    seen = set()
    for i, word in enumerate(obj):
        if word.pos not in (NOUN, PROPN, PRON):
            continue
        # Prevent nested chunks from being produced
        if word.i in seen:
            continue
        if word.dep in np_deps:
            if any(w.i in seen for w in word.subtree):
                continue
            seen.update(j for j in range(word.left_edge.i, word.right_edge.i+1))
            yield word.left_edge.i, word.right_edge.i+1, np_label
        elif word.dep == conj:
            head = word.head
            while head.dep == conj and head.head.i < head.i:
                head = head.head
            # If the head is an NP, and we're coordinated to it, we're an NP
            if head.dep in np_deps:
                if any(w.i in seen for w in word.subtree):
                    continue
                seen.update(j for j in range(word.left_edge.i, word.right_edge.i+1))
                yield word.left_edge.i, word.right_edge.i+1, np_label


SYNTAX_ITERATORS = {
    'noun_chunks': noun_chunks
}
