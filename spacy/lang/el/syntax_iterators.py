# coding: utf8
from __future__ import unicode_literals

from ...symbols import NOUN, PROPN, PRON


def noun_chunks(obj):
    """
    Detect base noun phrases. Works on both Doc and Span.
    """
    # It follows the logic of the noun chunks finder of English language,
    # adjusted to some Greek language special characteristics.
    # obj tag corrects some DEP tagger mistakes.
    # Further improvement of the models will eliminate the need for this tag.
    labels = ["nsubj", "obj", "iobj", "appos", "ROOT", "obl"]
    doc = obj.doc  # Ensure works on both Doc and Span.
    np_deps = [doc.vocab.strings.add(label) for label in labels]
    conj = doc.vocab.strings.add("conj")
    nmod = doc.vocab.strings.add("nmod")
    np_label = doc.vocab.strings.add("NP")
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
            flag = False
            if word.pos == NOUN:
                #  check for patterns such as γραμμή παραγωγής
                for potential_nmod in word.rights:
                    if potential_nmod.dep == nmod:
                        seen.update(
                            j for j in range(word.left_edge.i, potential_nmod.i + 1)
                        )
                        yield word.left_edge.i, potential_nmod.i + 1, np_label
                        flag = True
                        break
            if flag is False:
                seen.update(j for j in range(word.left_edge.i, word.i + 1))
                yield word.left_edge.i, word.i + 1, np_label
        elif word.dep == conj:
            # covers the case: έχει όμορφα και έξυπνα παιδιά
            head = word.head
            while head.dep == conj and head.head.i < head.i:
                head = head.head
            # If the head is an NP, and we're coordinated to it, we're an NP
            if head.dep in np_deps:
                if any(w.i in seen for w in word.subtree):
                    continue
                seen.update(j for j in range(word.left_edge.i, word.i + 1))
                yield word.left_edge.i, word.i + 1, np_label


SYNTAX_ITERATORS = {"noun_chunks": noun_chunks}
