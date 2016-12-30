from __future__ import unicode_literals
from collections import defaultdict
import numpy
import numpy.linalg
cimport numpy as np
from libc.math cimport sqrt
import six

from ..structs cimport TokenC, LexemeC
from ..typedefs cimport flags_t, attr_t, hash_t
from ..attrs cimport attr_id_t
from ..parts_of_speech cimport univ_pos_t
from ..util import normalize_slice
from .doc cimport token_by_start, token_by_end
from ..attrs cimport IS_PUNCT, IS_SPACE
from ..lexeme cimport Lexeme


cdef class Span:
    """A slice from a Doc object."""
    def __cinit__(self, Doc doc, int start, int end, int label=0, vector=None,
                  vector_norm=None):
        '''Create a Span object from the slice doc[start : end]

        Arguments:
            doc (Doc): The parent document.
            start (int): The index of the first token of the span.
            end (int): The index of the first token after the span.
            label (int): A label to attach to the Span, e.g. for named entities.
            vector (ndarray[ndim=1, dtype='float32']): A meaning representation of the span.
        Returns:
            Span The newly constructed object.
        '''
        if not (0 <= start <= end <= len(doc)):
            raise IndexError

        self.doc = doc
        self.start = start
        self.start_char = self.doc[start].idx if start < self.doc.length else 0
        self.end = end
        if end >= 1:
            self.end_char = self.doc[end - 1].idx + len(self.doc[end - 1])
        else:
            self.end_char = 0
        self.label = label
        self._vector = vector
        self._vector_norm = vector_norm

    def __richcmp__(self, Span other, int op):
        # Eq
        if op == 0:
            return self.start_char < other.start_char
        elif op == 1:
            return self.start_char <= other.start_char
        elif op == 2:
            return self.start_char == other.start_char and self.end_char == other.end_char
        elif op == 3:
            return self.start_char != other.start_char or self.end_char != other.end_char
        elif op == 4:
            return self.start_char > other.start_char
        elif op == 5:
            return self.start_char >= other.start_char

    def __len__(self):
        self._recalculate_indices()
        if self.end < self.start:
            return 0
        return self.end - self.start

    def __repr__(self):
        if six.PY3:
            return self.text
        return self.text.encode('utf-8')

    def __getitem__(self, object i):
        self._recalculate_indices()
        if isinstance(i, slice):
            start, end = normalize_slice(len(self), i.start, i.stop, i.step)
            return Span(self.doc, start + self.start, end + self.start)
        else:
            if i < 0:
                return self.doc[self.end + i]
            else:
                return self.doc[self.start + i]

    def __iter__(self):
        self._recalculate_indices()
        for i in range(self.start, self.end):
            yield self.doc[i]

    def merge(self, *args, **attributes):
        """Retokenize the document, such that the span is merged into a single token.

        Arguments:
            **attributes:
                Attributes to assign to the merged token. By default, attributes
                are inherited from the syntactic root token of the span.
        Returns:
            token (Token):
                The newly merged token.
        """
        return self.doc.merge(self.start_char, self.end_char, *args, **attributes)

    def similarity(self, other):
        '''Make a semantic similarity estimate. The default estimate is cosine
        similarity using an average of word vectors.

        Arguments:
            other (object): The object to compare with. By default, accepts Doc,
                Span, Token and Lexeme objects.

        Return:
            score (float): A scalar similarity score. Higher is more similar.
        '''
        if 'similarity' in self.doc.user_span_hooks:
            self.doc.user_span_hooks['similarity'](self, other)
        if self.vector_norm == 0.0 or other.vector_norm == 0.0:
            return 0.0
        return numpy.dot(self.vector, other.vector) / (self.vector_norm * other.vector_norm)

    cpdef int _recalculate_indices(self) except -1:
        if self.end > self.doc.length \
        or self.doc.c[self.start].idx != self.start_char \
        or (self.doc.c[self.end-1].idx + self.doc.c[self.end-1].lex.length) != self.end_char:
            start = token_by_start(self.doc.c, self.doc.length, self.start_char)
            if self.start == -1:
                raise IndexError("Error calculating span: Can't find start")
            end = token_by_end(self.doc.c, self.doc.length, self.end_char)
            if end == -1:
                raise IndexError("Error calculating span: Can't find end")
            
            self.start = start
            self.end = end + 1

    property sent:
        '''The sentence span that this span is a part of.
        
        Returns:
            Span The sentence this is part of.
        '''
        def __get__(self):
            if 'sent' in self.doc.user_span_hooks:
                return self.doc.user_span_hooks['sent'](self)
            # This should raise if we're not parsed.
            self.doc.sents
            cdef int n = 0
            root = &self.doc.c[self.start]
            while root.head != 0:
                root += root.head
                n += 1
                if n >= self.doc.length:
                    raise RuntimeError
            return self.doc[root.l_edge : root.r_edge + 1]

    property has_vector:
        def __get__(self):
            if 'has_vector' in self.doc.user_span_hooks:
                return self.doc.user_span_hooks['has_vector'](self)
            return any(token.has_vector for token in self)
    
    property vector:
        def __get__(self):
            if 'vector' in self.doc.user_span_hooks:
                return self.doc.user_span_hooks['vector'](self)
            if self._vector is None:
                self._vector = sum(t.vector for t in self) / len(self)
            return self._vector

    property vector_norm:
        def __get__(self):
            if 'vector_norm' in self.doc.user_span_hooks:
                return self.doc.user_span_hooks['vector'](self)
            cdef float value
            cdef double norm = 0
            if self._vector_norm is None:
                norm = 0
                for value in self.vector:
                    norm += value * value
                self._vector_norm = sqrt(norm) if norm != 0 else 0
            return self._vector_norm

    property sentiment:
        def __get__(self):
            if 'sentiment' in self.doc.user_span_hooks:
                return self.doc.user_span_hooks['sentiment'](self)
            else:
                return sum([token.sentiment for token in self]) / len(self)

    property text:
        def __get__(self):
            text = self.text_with_ws
            if self[-1].whitespace_:
                text = text[:-1]
            return text

    property text_with_ws:
        def __get__(self):
            return u''.join([t.text_with_ws for t in self])

    property noun_chunks:
        '''
        Yields base noun-phrase #[code Span] objects, if the document
        has been syntactically parsed. A base noun phrase, or 
        'NP chunk', is a noun phrase that does not permit other NPs to 
        be nested within it – so no NP-level coordination, no prepositional 
        phrases, and no relative clauses. For example:
        '''
        def __get__(self):
            if not self.doc.is_parsed:
                raise ValueError(
                    "noun_chunks requires the dependency parse, which "
                    "requires data to be installed. If you haven't done so, run: "
                    "\npython -m spacy.%s.download all\n"
                    "to install the data" % self.vocab.lang)
            # Accumulate the result before beginning to iterate over it. This prevents
            # the tokenisation from being changed out from under us during the iteration.
            # The tricky thing here is that Span accepts its tokenisation changing,
            # so it's okay once we have the Span objects. See Issue #375
            spans = []
            for start, end, label in self.doc.noun_chunks_iterator(self):
                spans.append(Span(self, start, end, label=label))
            for span in spans:
                yield span

    property root:
        """The token within the span that's highest in the parse tree. If there's a tie, the earlist is prefered.

        Returns:
            Token: The root token.
        
        i.e. has the
        shortest path to the root of the sentence (or is the root itself).

        If multiple words are equally high in the tree, the first word is taken.
        
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

        Here's a more complicated case, raise by Issue #214

        >>> toks = nlp(u'to, north and south carolina')
        >>> to, north, and_, south, carolina = toks
        >>> south.head.text, carolina.head.text
        ('north', 'to')

        Here 'south' is a child of 'north', which is a child of 'carolina'.
        Carolina is the root of the span:

        >>> south_carolina = toks[-2:]
        >>> south_carolina.root.text
        'carolina'
        """
        def __get__(self):
            self._recalculate_indices()
            if 'root' in self.doc.user_span_hooks:
                return self.doc.user_span_hooks['root'](self)
            # This should probably be called 'head', and the other one called
            # 'gov'. But we went with 'head' elsehwhere, and now we're stuck =/
            cdef int i
            # First, we scan through the Span, and check whether there's a word
            # with head==0, i.e. a sentence root. If so, we can return it. The
            # longer the span, the more likely it contains a sentence root, and
            # in this case we return in linear time.
            for i in range(self.start, self.end):
                if self.doc.c[i].head == 0:
                    return self.doc[i]
            # If we don't have a sentence root, we do something that's not so
            # algorithmically clever, but I think should be quite fast, especially
            # for short spans.
            # For each word, we count the path length, and arg min this measure.
            # We could use better tree logic to save steps here...But I think this
            # should be okay.
            cdef int current_best = self.doc.length
            cdef int root = -1
            for i in range(self.start, self.end):
                if self.start <= (i+self.doc.c[i].head) < self.end:
                    continue
                words_to_root = _count_words_to_root(&self.doc.c[i], self.doc.length)
                if words_to_root < current_best:
                    current_best = words_to_root
                    root = i
            if root == -1:
                return self.doc[self.start]
            else:
                return self.doc[root]
    
    property lefts:
        """Tokens that are to the left of the span, whose head is within the Span.
        
        Yields: Token A left-child of a token of the span.
        """
        def __get__(self):
            for token in reversed(self): # Reverse, so we get the tokens in order
                for left in token.lefts:
                    if left.i < self.start:
                        yield left

    property rights:
        """Tokens that are to the right of the Span, whose head is within the Span.
        
        Yields: Token A right-child of a token of the span.
        """
        def __get__(self):
            for token in self:
                for right in token.rights:
                    if right.i >= self.end:
                        yield right

    property subtree:
        """Tokens that descend from tokens in the span, but fall outside it.

        Yields: Token A descendant of a token within the span.
        """
        def __get__(self):
            for word in self.lefts:
                yield from word.subtree
            yield from self
            for word in self.rights:
                yield from word.subtree

    property ent_id:
        '''An (integer) entity ID. Usually assigned by patterns in the Matcher.'''
        def __get__(self):
            return self.root.ent_id

        def __set__(self, hash_t key):
            # TODO
            raise NotImplementedError(
                "Can't yet set ent_id from Span. Vote for this feature on the issue "
                "tracker: http://github.com/spacy-io/spaCy")
    property ent_id_:
        '''A (string) entity ID. Usually assigned by patterns in the Matcher.'''
        def __get__(self):
            return self.root.ent_id_

        def __set__(self, hash_t key):
            # TODO
            raise NotImplementedError(
                "Can't yet set ent_id_ from Span. Vote for this feature on the issue "
                "tracker: http://github.com/spacy-io/spaCy")

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


cdef int _count_words_to_root(const TokenC* token, int sent_length) except -1:
    # Don't allow spaces to be the root, if there are
    # better candidates
    if Lexeme.c_check_flag(token.lex, IS_SPACE) and token.l_kids == 0 and token.r_kids == 0:
        return sent_length-1
    if Lexeme.c_check_flag(token.lex, IS_PUNCT) and token.l_kids == 0 and token.r_kids == 0:
        return sent_length-1
    cdef int n = 0
    while token.head != 0:
        token += token.head
        n += 1
        if n >= sent_length:
            raise RuntimeError(
                "Array bounds exceeded while searching for root word. This likely "
                "means the parse tree is in an invalid state. Please report this "
                "issue here: http://github.com/honnibal/spaCy/")
    return n
