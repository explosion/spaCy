from spacy.parts_of_speech cimport NOUN, PROPN, PRON


def english_noun_chunks(obj):
    '''Detect base noun phrases from a dependency parse.
    Works on both Doc and Span.'''
    labels = ['nsubj', 'dobj', 'nsubjpass', 'pcomp', 'pobj',
              'attr', 'ROOT', 'root']
    doc = obj.doc # Ensure works on both Doc and Span.
    np_deps = [doc.vocab.strings[label] for label in labels]
    conj = doc.vocab.strings['conj']
    np_label = doc.vocab.strings['NP']
    for i, word in enumerate(obj):
        if word.pos in (NOUN, PROPN, PRON) and word.dep in np_deps:
            yield word.left_edge.i, word.i+1, np_label
        elif word.pos == NOUN and word.dep == conj:
            head = word.head
            while head.dep == conj and head.head.i < head.i:
                head = head.head
            # If the head is an NP, and we're coordinated to it, we're an NP
            if head.dep in np_deps:
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


CHUNKERS = {'en': english_noun_chunks, 'de': german_noun_chunks}
