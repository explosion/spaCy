from __future__ import unicode_literals
from collections import defaultdict


cdef class Span:
    """A slice from a Tokens object."""
    def __cinit__(self, Tokens tokens, int start, int end, int label=0):
        self._seq = tokens
        self.start = start
        self.end = end
        self.label = label
        self.head = self

        self.rights = []
        self.lefts = []

    def __richcmp__(self, Span other, int op):
        # Eq
        if op == 0:
            return self.start < other.start
        elif op == 1:
            return self.start <= other.start
        elif op == 2:
            return self.start == other.start and self.end == other.end
        elif op == 3:
            return self.start != other.start or self.end != other.end
        elif op == 4:
            return self.start > other.start
        elif op == 5:
            return self.start >= other.start

    def __len__(self):
        if self.end < self.start:
            return 0
        return self.end - self.start

    def __getitem__(self, int i):
        return self._seq[self.start + i]

    def __iter__(self):
        for i in range(self.start, self.end):
            yield self._seq[i]

    property orth_:
        def __get__(self):
            return ''.join([t.string for t in self]).strip()

    property lemma_:
        def __get__(self):
            return ' '.join([t.lemma_ for t in self]).strip()

    property string:
        def __get__(self):
            return ''.join([t.string for t in self])

    property label_:
        def __get__(self):
            return self._seq.vocab.strings[self.label]

    property subtree:
        def __get__(self):
            for word in self.lefts:
                yield from word.subtree
            yield self
            for word in self.rights:
                yield from word.subtree
