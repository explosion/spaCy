from __future__ import unicode_literals
from collections import defaultdict


cdef class Spans:
    def __init__(self, Tokens tokens, merge_ents=True, mwe_re=None):
        self.tokens = tokens
        # Initialize spans as one per token
        self.spans = [Span(self.tokens, i, i+1) for i in range(len(tokens))]
        self.vocab = tokens.vocab
        if mwe_re is not None:
            token_starts = {t.idx: t.i for t in self.tokens}
            token_ends = {t.idx + len(t): t.i+1 for t in self.tokens}
            tokens_str = unicode(self.tokens)
            for label, regex in mwe_re:
                for match in regex.finditer(tokens_str):
                    start = token_starts.get(match.start())
                    end = token_ends.get(match.end())
                    self.merge(start, end, label=label)
        if merge_ents:
            # Merge named entities and units
            for ent in self.tokens.ents:
                self.merge(ent.start, ent.end, label=ent.label)
        
    def merge(self, int start, int end, object label=0):
        if type(label) == unicode:
            label = self.vocab.strings[label]
        new_spans = [s for s in self.spans if s.end <= start]
        new_span = Span(self.tokens, start, end, label=label)
        new_spans.append(new_span)
        new_spans.extend(s for s in self.spans if s.start >= end)
        self.spans = new_spans
        _assign_indices(self.spans)
        _assign_heads(self.spans)
        return new_span

    def __getitem__(self, int i):
        return self.spans[i]

    def __iter__(self):
        yield from self.spans

    def __len__(self):
        return len(self.spans)

    def __unicode__(self):
        pass

    def count_by(self, attr_id_t attr_id, exclude=None):
        return self.tokens.count_by(attr_id, exclude=exclude)

    property sents:
        def __get__(self):
            yield from self.tokens.sents

    property ents:
        def __get__(self):
            yield from self.tokens.ents

    cpdef long[:,:] to_array(self, object py_attr_ids):
        return self.tokens.to_array(py_attr_ids)

def _assign_indices(spans):
    for i, span in enumerate(spans):
        span.i = i

def _assign_heads(spans):
    spans_by_token = {}
    for span in spans:
        for i in range(span.start, span.end):
            spans_by_token[i] = span
    for span in spans:
        heads = defaultdict(int)
        for token in span:
            head_span = spans_by_token[token.head.i]
            if head_span is not span:
                heads[head_span.i] += 1
        if heads:
            span.head = spans[max(heads.items(), key=lambda i: i[1])[0]]
        else:
            span.head = span
        span.lefts = []
        span.rights = []
    for span in spans:
        if span < span.head:
            span.head.lefts.append(span)
        elif span.head.i != span.i:
            span.head.rights.append(span)


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
            return ' '.join([t.string for t in self]).strip()

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
