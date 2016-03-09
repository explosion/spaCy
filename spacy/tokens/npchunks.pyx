
from ..structs cimport TokenC
from .doc cimport Doc
from .span cimport Span

from ..parts_of_speech cimport NOUN, PROPN, PRON

def english(Span sent):
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


def german(Span sent):
    # this function extracts spans headed by NOUNs starting from the left-most
    # syntactic dependent until the NOUN itself
    # for close apposition and measurement construction, the span is sometimes
    # extended to the right of the NOUN
    # example: "eine Tasse Tee" (a cup (of) tea) returns "eine Tasse Tee" and not
    # just "eine Tasse", same for "das Thema Familie"
    cdef const TokenC* word
    strings = sent.doc.vocab.strings
    labels = ['sb', 'oa', 'da', 'nk', 'mo', 'ag', 'root', 'cj', 'pd', 'og', 'app']
    close_app = strings['nk']
    np_deps = [strings[label] for label in labels]
    np_label = strings['NP']
    for i in range(sent.start, sent.end):
        word = &sent.doc.c[i]
        if word.pos == NOUN and word.dep in np_deps:
            rbracket = i+1
            # try to extend the span to the right
            # to capture close apposition/measurement constructions
            for rdep in sent.doc[i].rights:
                if rdep.pos == NOUN and rdep.dep == close_app:
                    rbracket = rdep.i+1
            yield Span(sent.doc, word.l_edge, rbracket, label=np_label)




