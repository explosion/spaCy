# coding: utf-8
from __future__ import unicode_literals

from ..parts_of_speech cimport NOUN, PROPN, PRON, VERB, AUX


def english_noun_chunks(obj):
    """
    Detect base noun phrases from a dependency parse.
    Works on both Doc and Span.
    """
    labels = ['nsubj', 'dobj', 'nsubjpass', 'pcomp', 'pobj',
              'attr', 'ROOT']
    doc = obj.doc # Ensure works on both Doc and Span.
    np_deps = [doc.vocab.strings[label] for label in labels]
    conj = doc.vocab.strings['conj']
    np_label = doc.vocab.strings['NP']
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
            seen.update(j for j in range(word.left_edge.i, word.i+1))
            yield word.left_edge.i, word.i+1, np_label
        elif word.dep == conj:
            head = word.head
            while head.dep == conj and head.head.i < head.i:
                head = head.head
            # If the head is an NP, and we're coordinated to it, we're an NP
            if head.dep in np_deps:
                if any(w.i in seen for w in word.subtree):
                    continue
                seen.update(j for j in range(word.left_edge.i, word.i+1))
                yield word.left_edge.i, word.i+1, np_label


# this iterator extracts spans headed by NOUNs starting from the left-most
# syntactic dependent until the NOUN itself
# for close apposition and measurement construction, the span is sometimes
# extended to the right of the NOUN
# example: "eine Tasse Tee" (a cup (of) tea) returns "eine Tasse Tee" and not
# just "eine Tasse", same for "das Thema Familie"
def german_noun_chunks(obj):
    labels = ['sb', 'oa', 'da', 'nk', 'mo', 'ag', 'ROOT', 'root', 'cj', 'pd', 'og', 'app']
    doc = obj.doc # Ensure works on both Doc and Span.
    np_label = doc.vocab.strings['NP']
    np_deps = set(doc.vocab.strings[label] for label in labels)
    close_app = doc.vocab.strings['nk']

    rbracket = 0
    for i, word in enumerate(obj):
        if i < rbracket:
            continue
        if word.pos in (NOUN, PROPN, PRON) and word.dep in np_deps:
            rbracket = word.i+1
            # try to extend the span to the right
            # to capture close apposition/measurement constructions
            for rdep in doc[word.i].rights:
                if rdep.pos in (NOUN, PROPN) and rdep.dep == close_app:
                    rbracket = rdep.i+1
            yield word.left_edge.i, rbracket, np_label


def es_noun_chunks(obj):

    doc = obj.doc
    np_label = doc.vocab.strings['NP']

    left_labels = ['det', 'fixed', 'neg'] #['nunmod', 'det', 'appos', 'fixed']
    right_labels = ['flat', 'fixed', 'compound', 'neg']
    stop_labels = ['punct']

    np_left_deps = [doc.vocab.strings[label] for label in left_labels]
    np_right_deps = [doc.vocab.strings[label] for label in right_labels]
    stop_deps = [doc.vocab.strings[label] for label in stop_labels]

    def next_token(token):
        try:
            return token.nbor()
        except:
            return None

    def noun_bounds(root):

        def is_verb_token(token):
            return token.pos in [VERB, AUX]

        left_bound = root
        for token in reversed(list(root.lefts)):
            if token.dep in np_left_deps:
                left_bound = token

        right_bound = root
        for token in root.rights:
            if (token.dep in np_right_deps):
                left, right = noun_bounds(token)

                if list(filter(lambda t: is_verb_token(t) or t.dep in stop_deps, doc[left_bound.i: right.i])):
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


CHUNKERS = {'en': english_noun_chunks, 'de': german_noun_chunks, 'es': es_noun_chunks}
