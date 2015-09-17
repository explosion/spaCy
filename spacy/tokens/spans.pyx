from __future__ import unicode_literals
from collections import defaultdict
import numpy
import numpy.linalg
cimport numpy as np
import math

from ..structs cimport TokenC, LexemeC
from ..typedefs cimport flags_t, attr_t
from ..attrs cimport attr_id_t
from ..parts_of_speech cimport univ_pos_t


cdef class Span:
    """A slice from a Doc object."""
    def __cinit__(self, Doc tokens, int start, int end, int label=0):
        if start < 0:
            start = tokens.length - start
        if end < 0:
            end = tokens.length - end
        self._seq = tokens
        self.start = start
        self.end = end
        self.label = label
        self._vector = None
        self._vector_norm = None

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
        if i < 0:
            return self._seq[self.end + i]
        else:
            return self._seq[self.start + i]

    def __iter__(self):
        for i in range(self.start, self.end):
            yield self._seq[i]

    def merge(self, unicode tag, unicode lemma, unicode ent_type):
        self._seq.merge(self[0].idx, self[-1].idx + len(self[-1]), tag, lemma, ent_type)

    def similarity(self, other):
        return numpy.dot(self.vector, other.vector) / (self.vector_norm * other.vector_norm)

    property vector:
        def __get__(self):
            if self._vector is None:
                self._vector = sum(t.vector for t in self) / len(self)
            return self._vector

        def __set__(self, value):
            self._vector = value

    property vector_norm:
        def __get__(self):
            cdef float value
            if self._vector_norm is None:
                self._vector_norm = 1e-20
                for value in self.vector:
                    self._vector_norm += value * value
                self._vector_norm = math.sqrt(self._vector_norm)
            return self._vector_norm
    
        def __set__(self, value):
            self._vector_norm = value

    property text:
        def __get__(self):
            text = self.text_with_ws
            if self[-1].whitespace_:
                text = text[:-1]
            return text

    property text_with_ws:
        def __get__(self):
            return u''.join([t.text_with_ws for t in self])

    property root:
        """The first ancestor of the first word of the span that has its head
        outside the span.
        
        For example:
        
        >>> toks = nlp(u'I like New York in Autumn.')

        Let's name the indices --- easier than writing "toks[4]" etc.

        >>> i, like, new, york, in_, autumn, dot = range(len(toks)) 

        The head of 'new' is 'York', and the head of 'York' is 'like'

        >>> toks[new].head.orth_
        'York'
        >>> toks[york].head.orth_
        'like'

        Create a span for "New York". Its root is "York".

        >>> new_york = toks[new:york+1]
        >>> new_york.root.orth_
        'York'

        When there are multiple words with external dependencies, we take the first:

        >>> toks[autumn].head.orth_, toks[dot].head.orth_
        ('in', like')
        >>> autumn_dot = toks[autumn:]
        >>> autumn_dot.root.orth_
        'Autumn'
        """
        def __get__(self):
            # This should probably be called 'head', and the other one called
            # 'gov'. But we went with 'head' elsehwhere, and now we're stuck =/
            cdef const TokenC* start = &self._seq.data[self.start]
            cdef const TokenC* end = &self._seq.data[self.end]
            head = start
            while start <= (head + head.head) < end and head.head != 0:
                head += head.head
            return self._seq[head - self._seq.data]

    property lefts:
        """Tokens that are to the left of the Span, whose head is within the Span."""
        def __get__(self):
            for token in reversed(self): # Reverse, so we get the tokens in order
                for left in token.lefts:
                    if left.i < self.start:
                        yield left

    property rights:
        """Tokens that are to the right of the Span, whose head is within the Span."""
        def __get__(self):
            for token in self:
                for right in token.rights:
                    if right.i >= self.end:
                        yield right

    property subtree:
        def __get__(self):
            for word in self.lefts:
                yield from word.subtree
            yield from self
            for word in self.rights:
                yield from word.subtree

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

