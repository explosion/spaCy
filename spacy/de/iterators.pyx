from spacy.structs cimport TokenC
from spacy.tokens.span cimport Span

from spacy.parts_of_speech cimport NOUN

def noun_chunks(Span sent):
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
