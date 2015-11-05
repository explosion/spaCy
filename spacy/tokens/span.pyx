from __future__ import unicode_literals
from collections import defaultdict
import numpy
import numpy.linalg
cimport numpy as np
import math
import six

from ..structs cimport TokenC, LexemeC
from ..typedefs cimport flags_t, attr_t
from ..attrs cimport attr_id_t
from ..parts_of_speech cimport univ_pos_t
from ..util import normalize_slice


cdef class Span:
    """A slice from a Doc object."""
    def __cinit__(self, Doc tokens, int start, int end, int label=0, vector=None,
                  vector_norm=None):
        if not (0 <= start <= end <= len(tokens)):
            raise IndexError

        self.doc = tokens
        self.start_token = start
        self.start_idx = self.doc[start].idx
        self.end_token = end
        self.end_idx = self.doc[end - 1].idx + len(self.doc[end - 1])
        self.label = label
        self._vector = vector
        self._vector_norm = vector_norm

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

    def __repr__(self):
        if six.PY3:
            return self.text
        return self.text.encode('utf-8')

    def __getitem__(self, object i):
        if isinstance(i, slice):
            start, end = normalize_slice(len(self), i.start, i.stop, i.step)
            start += self.start
            end += self.start
            return Span(self.doc, start, end)

        if i < 0:
            return self.doc[self.end + i]
        else:
            return self.doc[self.start + i]

    def __iter__(self):
        for i in range(self.start, self.end):
            yield self.doc[i]

    def merge(self, unicode tag, unicode lemma, unicode ent_type):
        self.doc.merge(self[0].idx, self[-1].idx + len(self[-1]), tag, lemma, ent_type)

    def similarity(self, other):
        if self.vector_norm == 0.0 or other.vector_norm == 0.0:
            return 0.0
        return numpy.dot(self.vector, other.vector) / (self.vector_norm * other.vector_norm)

    property start:
        """ Get start token index of this span from the Doc."""
        def __get__(self):
            # first is the first token of the span - get it from the doc
            first = None
            if self.start_token < len(self.doc):
                first = self.doc[self.start_token]
            # if we have merged spans in Doc start might have changed.
            # check if token start index is in doc index range and the token
            # index is start_idx (it hasn't changed).
            if first is None or first.idx != self.start_idx:
                # go through tokens in Doc - find index of token equal to start_idx
                new_start = self.doc.token_index_start(self.start_idx)
                if new_start is not None:
                    self.start_token = new_start
                else:
                    raise IndexError('Something went terribly wrong during a merge.'
                                     'No token found with idx %s' % self.start_idx)
            return self.start_token

    property end:
        """ Get end token index of this span from the Doc."""
        def __get__(self):
            # last is the last token of the span - get it from the doc
            last = None
            if self.end_token <= len(self.doc):
                last = self.doc[self.end_token -1]
            # if we have merged spans in Doc end will have changed.
            # check if token end index is in doc index range and the token
            # index is end_idx + len(last_token) (it hasn't changed).
            if last is None or last.idx + len(last) != self.end_idx:
                # go through tokens in Doc - find index of token equal to end_idx
                new_end = self.doc.token_index_end(self.end_idx)
                if new_end is not None:
                    self.end_token = new_end
                else:
                    raise IndexError('Something went terribly wrong during a merge.'
                                     'No token found with idx %s' % self.end_idx)
            return self.end_token

    property vector:
        def __get__(self):
            if self._vector is None:
                self._vector = sum(t.vector for t in self) / len(self)
            return self._vector

    property vector_norm:
        def __get__(self):
            cdef float value
            if self._vector_norm is None:
                self._vector_norm = 1e-20
                for value in self.vector:
                    self._vector_norm += value * value
                self._vector_norm = math.sqrt(self._vector_norm)
            return self._vector_norm

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
            cdef const TokenC* start = &self.doc.c[self.start]
            cdef const TokenC* end = &self.doc.c[self.end]
            head = start
            while start <= (head + head.head) < end and head.head != 0:
                head += head.head
            return self.doc[head - self.doc.c]

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
            return self.doc.vocab.strings[self.label]

