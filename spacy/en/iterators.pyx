from spacy.structs cimport TokenC
from spacy.tokens.span cimport Span

from spacy.parts_of_speech cimport NOUN

def noun_chunks(Span sent):
    cdef const TokenC* word
    strings = sent.doc.vocab.strings
    labels = ['nsubj', 'dobj', 'nsubjpass', 'pcomp', 'pobj', 'attr', 'root']
    np_deps = [strings[label] for label in labels]
    conj = strings['conj']
    np_label = strings['NP']
    for i in range(sent.start, sent.end):
        word = &sent.doc.c[i]
        if word.pos == NOUN and word.dep in np_deps:
            yield Span(sent.doc, word.l_edge, i+1, label=np_label)
        elif word.pos == NOUN and word.dep == conj:
            head = word+word.head
            while head.dep == conj and head.head < 0:
                head += head.head
            # If the head is an NP, and we're coordinated to it, we're an NP
            if head.dep in np_deps:
                yield Span(sent.doc, word.l_edge, i+1, label=np_label)

