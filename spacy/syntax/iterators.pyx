from spacy.structs cimport TokenC
from spacy.tokens.span cimport Span
from spacy.tokens.doc cimport Doc
from spacy.tokens.token cimport Token

from spacy.parts_of_speech cimport NOUN

CHUNKERS = {'en':EnglishNounChunks, 'de':GermanNounChunks}

# base class for document iterators
cdef class DocIterator:
    def __init__(self, Doc doc):
        self._doc = doc

    def __iter__(self):
        return self

    def __next__(self):
        raise NotImplementedError


cdef class EnglishNounChunks(DocIterator):
    def __init__(self, Doc doc):
        super(EnglishNounChunks,self).__init__(doc)
        labels = ['nsubj', 'dobj', 'nsubjpass', 'pcomp', 'pobj', 'attr', 'root']
        self._np_label = self._doc.vocab.strings['NP']
        self._np_deps = set( self._doc.vocab.strings[label] for label in labels )
        self._conjunct = self._doc.vocab.strings['conj']
        self.i = 0

    def __next__(self):
        cdef const TokenC* word
        cdef widx
        while self.i < self._doc.length:
            widx = self.i
            self.i += 1
            word = &self._doc.c[widx]
            if word.pos == NOUN:
                if word.dep in self._np_deps:
                    return Span(self._doc, word.l_edge, widx+1, label=self._np_label)
                elif word.dep == self._conjunct:
                    head = word+word.head
                    while head.dep == self._conjunct and head.head < 0:
                        head += head.head
                    # If the head is an NP, and we're coordinated to it, we're an NP
                    if head.dep in self._np_deps:
                        return Span(self._doc, word.l_edge, widx+1, label=self._np_label)
        raise StopIteration


# this iterator extracts spans headed by NOUNs starting from the left-most
# syntactic dependent until the NOUN itself
# for close apposition and measurement construction, the span is sometimes
# extended to the right of the NOUN
# example: "eine Tasse Tee" (a cup (of) tea) returns "eine Tasse Tee" and not
# just "eine Tasse", same for "das Thema Familie"
cdef class GermanNounChunks(DocIterator):
    def __init__(self, Doc doc):
        super(GermanNounChunks,self).__init__(doc)
        labels = ['sb', 'oa', 'da', 'nk', 'mo', 'ag', 'root', 'cj', 'pd', 'og', 'app']
        self._np_label = self._doc.vocab.strings['NP']
        self._np_deps = set( self._doc.vocab.strings[label] for label in labels )
        self._close_app = self._doc.vocab.strings['nk']
        self.i = 0

    def __next__(self):
        cdef const TokenC* word
        cdef int rbracket
        cdef Token rdep
        cdef widx
        while self.i < self._doc.length:
            widx = self.i
            self.i += 1
            word = &self._doc.c[widx]
            if word.pos == NOUN and word.dep in self._np_deps:
                rbracket = widx+1
                # try to extend the span to the right
                # to capture close apposition/measurement constructions
                for rdep in self._doc[widx].rights:
                    if rdep.pos == NOUN and rdep.dep == self._close_app:
                        rbracket = rdep.i+1
                return Span(self._doc, word.l_edge, rbracket, label=self._np_label)                
        raise StopIteration

