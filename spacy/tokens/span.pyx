# coding: utf8
from __future__ import unicode_literals

cimport numpy as np
from libc.math cimport sqrt

import numpy
import numpy.linalg
from thinc.neural.util import get_array_module
from collections import defaultdict

from .doc cimport token_by_start, token_by_end, get_token_attr, _get_lca_matrix
from .token cimport TokenC
from ..structs cimport TokenC, LexemeC
from ..typedefs cimport flags_t, attr_t, hash_t
from ..attrs cimport attr_id_t
from ..parts_of_speech cimport univ_pos_t
from ..attrs cimport *
from ..lexeme cimport Lexeme

from ..util import normalize_slice
from ..compat import is_config, basestring_
from ..errors import Errors, TempErrors, Warnings, user_warning, models_warning
from ..errors import deprecation_warning
from .underscore import Underscore, get_ext_args


cdef class Span:
    """A slice from a Doc object.

    DOCS: https://spacy.io/api/span
    """
    @classmethod
    def set_extension(cls, name, **kwargs):
        """Define a custom attribute which becomes available as `Span._`.

        name (unicode): Name of the attribute to set.
        default: Optional default value of the attribute.
        getter (callable): Optional getter function.
        setter (callable): Optional setter function.
        method (callable): Optional method for method extension.
        force (bool): Force overwriting existing attribute.

        DOCS: https://spacy.io/api/span#set_extension
        USAGE: https://spacy.io/usage/processing-pipelines#custom-components-attributes
        """
        if cls.has_extension(name) and not kwargs.get("force", False):
            raise ValueError(Errors.E090.format(name=name, obj="Span"))
        Underscore.span_extensions[name] = get_ext_args(**kwargs)

    @classmethod
    def get_extension(cls, name):
        """Look up a previously registered extension by name.

        name (unicode): Name of the extension.
        RETURNS (tuple): A `(default, method, getter, setter)` tuple.

        DOCS: https://spacy.io/api/span#get_extension
        """
        return Underscore.span_extensions.get(name)

    @classmethod
    def has_extension(cls, name):
        """Check whether an extension has been registered.

        name (unicode): Name of the extension.
        RETURNS (bool): Whether the extension has been registered.

        DOCS: https://spacy.io/api/span#has_extension
        """
        return name in Underscore.span_extensions

    @classmethod
    def remove_extension(cls, name):
        """Remove a previously registered extension.

        name (unicode): Name of the extension.
        RETURNS (tuple): A `(default, method, getter, setter)` tuple of the
            removed extension.

        DOCS: https://spacy.io/api/span#remove_extension
        """
        if not cls.has_extension(name):
            raise ValueError(Errors.E046.format(name=name))
        return Underscore.span_extensions.pop(name)

    def __cinit__(self, Doc doc, int start, int end, label=0, vector=None,
                  vector_norm=None, kb_id=0):
        """Create a `Span` object from the slice `doc[start : end]`.

        doc (Doc): The parent document.
        start (int): The index of the first token of the span.
        end (int): The index of the first token after the span.
        label (uint64): A label to attach to the Span, e.g. for named entities.
        kb_id (uint64): An identifier from a Knowledge Base to capture the meaning of a named entity.
        vector (ndarray[ndim=1, dtype='float32']): A meaning representation
            of the span.
        RETURNS (Span): The newly constructed object.

        DOCS: https://spacy.io/api/span#init
        """
        if not (0 <= start <= end <= len(doc)):
            raise IndexError(Errors.E035.format(start=start, end=end, length=len(doc)))
        self.doc = doc
        self.start = start
        self.start_char = self.doc[start].idx if start < self.doc.length else 0
        self.end = end
        if end >= 1:
            self.end_char = self.doc[end - 1].idx + len(self.doc[end - 1])
        else:
            self.end_char = 0
        if isinstance(label, basestring_):
            label = doc.vocab.strings.add(label)
        if isinstance(kb_id, basestring_):
            kb_id = doc.vocab.strings.add(kb_id)
        if label not in doc.vocab.strings:
            raise ValueError(Errors.E084.format(label=label))
        self.label = label
        self._vector = vector
        self._vector_norm = vector_norm
        self.kb_id = kb_id

    def __richcmp__(self, Span other, int op):
        if other is None:
            if op == 0 or op == 1 or op == 2:
                return False
            else:
                return True
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

    def __hash__(self):
        return hash((self.doc, self.label, self.start_char, self.end_char))

    def __len__(self):
        """Get the number of tokens in the span.

        RETURNS (int): The number of tokens in the span.

        DOCS: https://spacy.io/api/span#len
        """
        self._recalculate_indices()
        if self.end < self.start:
            return 0
        return self.end - self.start

    def __repr__(self):
        if is_config(python3=True):
            return self.text
        return self.text.encode("utf-8")

    def __getitem__(self, object i):
        """Get a `Token` or a `Span` object

        i (int or tuple): The index of the token within the span, or slice of
            the span to get.
        RETURNS (Token or Span): The token at `span[i]`.

        DOCS: https://spacy.io/api/span#getitem
        """
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
        """Iterate over `Token` objects.

        YIELDS (Token): A `Token` object.

        DOCS: https://spacy.io/api/span#iter
        """
        self._recalculate_indices()
        for i in range(self.start, self.end):
            yield self.doc[i]

    def __reduce__(self):
        raise NotImplementedError(Errors.E112)

    @property
    def _(self):
        """Custom extension attributes registered via `set_extension`."""
        return Underscore(Underscore.span_extensions, self,
                          start=self.start_char, end=self.end_char)

    def as_doc(self):
        """Create a `Doc` object with a copy of the `Span`'s data.

        RETURNS (Doc): The `Doc` copy of the span.

        DOCS: https://spacy.io/api/span#as_doc
        """
        # TODO: Fix!
        words = [t.text for t in self]
        spaces = [bool(t.whitespace_) for t in self]
        cdef Doc doc = Doc(self.doc.vocab, words=words, spaces=spaces)
        array_head = [LENGTH, SPACY, LEMMA, ENT_IOB, ENT_TYPE]
        if self.doc.is_tagged:
            array_head.append(TAG)
        # If doc parsed add head and dep attribute
        if self.doc.is_parsed:
            array_head.extend([HEAD, DEP])
        # Otherwise add sent_start
        else:
            array_head.append(SENT_START)
        array = self.doc.to_array(array_head)
        doc.from_array(array_head, array[self.start : self.end])
        doc.noun_chunks_iterator = self.doc.noun_chunks_iterator
        doc.user_hooks = self.doc.user_hooks
        doc.user_span_hooks = self.doc.user_span_hooks
        doc.user_token_hooks = self.doc.user_token_hooks
        doc.vector = self.vector
        doc.vector_norm = self.vector_norm
        doc.tensor = self.doc.tensor[self.start : self.end]
        for key, value in self.doc.cats.items():
            if hasattr(key, "__len__") and len(key) == 3:
                cat_start, cat_end, cat_label = key
                if cat_start == self.start_char and cat_end == self.end_char:
                    doc.cats[cat_label] = value
        return doc

    def merge(self, *args, **attributes):
        """Retokenize the document, such that the span is merged into a single
        token.

        **attributes: Attributes to assign to the merged token. By default,
            attributes are inherited from the syntactic root token of the span.
        RETURNS (Token): The newly merged token.
        """
        deprecation_warning(Warnings.W013.format(obj="Span"))
        return self.doc.merge(self.start_char, self.end_char, *args,
                              **attributes)

    def get_lca_matrix(self):
        """Calculates a matrix of Lowest Common Ancestors (LCA) for a given
        `Span`, where LCA[i, j] is the index of the lowest common ancestor among
        the tokens span[i] and span[j]. If they have no common ancestor within
        the span, LCA[i, j] will be -1.

        RETURNS (np.array[ndim=2, dtype=numpy.int32]): LCA matrix with shape
            (n, n), where n = len(self).

        DOCS: https://spacy.io/api/span#get_lca_matrix
        """
        return numpy.asarray(_get_lca_matrix(self.doc, self.start, self.end))

    def similarity(self, other):
        """Make a semantic similarity estimate. The default estimate is cosine
        similarity using an average of word vectors.

        other (object): The object to compare with. By default, accepts `Doc`,
            `Span`, `Token` and `Lexeme` objects.
        RETURNS (float): A scalar similarity score. Higher is more similar.

        DOCS: https://spacy.io/api/span#similarity
        """
        if "similarity" in self.doc.user_span_hooks:
            self.doc.user_span_hooks["similarity"](self, other)
        if len(self) == 1 and hasattr(other, "orth"):
            if self[0].orth == other.orth:
                return 1.0
        elif hasattr(other, "__len__") and len(self) == len(other):
            for i in range(len(self)):
                if self[i].orth != getattr(other[i], "orth", None):
                    break
            else:
                return 1.0
        if self.vocab.vectors.n_keys == 0:
            models_warning(Warnings.W007.format(obj="Span"))
        if self.vector_norm == 0.0 or other.vector_norm == 0.0:
            user_warning(Warnings.W008.format(obj="Span"))
            return 0.0
        vector = self.vector
        xp = get_array_module(vector)
        return xp.dot(vector, other.vector) / (self.vector_norm * other.vector_norm)

    cpdef np.ndarray to_array(self, object py_attr_ids):
        """Given a list of M attribute IDs, export the tokens to a numpy
        `ndarray` of shape `(N, M)`, where `N` is the length of the document.
        The values will be 32-bit integers.

        attr_ids (list[int]): A list of attribute ID ints.
        RETURNS (numpy.ndarray[long, ndim=2]): A feature matrix, with one row
            per word, and one column per attribute indicated in the input
            `attr_ids`.
        """
        cdef int i, j
        cdef attr_id_t feature
        cdef np.ndarray[attr_t, ndim=2] output
        # Make an array from the attributes - otherwise our inner loop is Python
        # dict iteration
        cdef np.ndarray[attr_t, ndim=1] attr_ids = numpy.asarray(py_attr_ids, dtype=numpy.uint64)
        cdef int length = self.end - self.start
        output = numpy.ndarray(shape=(length, len(attr_ids)), dtype=numpy.uint64)
        for i in range(self.start, self.end):
            for j, feature in enumerate(attr_ids):
                output[i-self.start, j] = get_token_attr(&self.doc.c[i], feature)
        return output

    cpdef int _recalculate_indices(self) except -1:
        if self.end > self.doc.length \
        or self.doc.c[self.start].idx != self.start_char \
        or (self.doc.c[self.end-1].idx + self.doc.c[self.end-1].lex.length) != self.end_char:
            start = token_by_start(self.doc.c, self.doc.length, self.start_char)
            if self.start == -1:
                raise IndexError(Errors.E036.format(start=self.start_char))
            end = token_by_end(self.doc.c, self.doc.length, self.end_char)
            if end == -1:
                raise IndexError(Errors.E037.format(end=self.end_char))
            self.start = start
            self.end = end + 1

    @property
    def vocab(self):
        """RETURNS (Vocab): The Span's Doc's vocab."""
        return self.doc.vocab

    @property
    def sent(self):
        """RETURNS (Span): The sentence span that the span is a part of."""
        if "sent" in self.doc.user_span_hooks:
            return self.doc.user_span_hooks["sent"](self)
        # This should raise if not parsed / no custom sentence boundaries
        self.doc.sents
        # If doc is parsed we can use the deps to find the sentence
        # otherwise we use the `sent_start` token attribute
        cdef int n = 0
        cdef int i
        if self.doc.is_parsed:
            root = &self.doc.c[self.start]
            while root.head != 0:
                root += root.head
                n += 1
                if n >= self.doc.length:
                    raise RuntimeError(Errors.E038)
            return self.doc[root.l_edge:root.r_edge + 1]
        elif self.doc.is_sentenced:
            # Find start of the sentence
            start = self.start
            while self.doc.c[start].sent_start != 1 and start > 0:
                start += -1
            # Find end of the sentence
            end = self.end
            n = 0
            while end < self.doc.length and self.doc.c[end].sent_start != 1:
                end += 1
                n += 1
                if n >= self.doc.length:
                    break
            return self.doc[start:end]

    @property
    def ents(self):
        """The named entities in the span. Returns a tuple of named entity
        `Span` objects, if the entity recognizer has been applied.

        RETURNS (tuple): Entities in the span, one `Span` per entity.

        DOCS: https://spacy.io/api/span#ents
        """
        ents = []
        for ent in self.doc.ents:
            if ent.start >= self.start and ent.end <= self.end:
                ents.append(ent)
        return ents

    @property
    def has_vector(self):
        """A boolean value indicating whether a word vector is associated with
        the object.

        RETURNS (bool): Whether a word vector is associated with the object.

        DOCS: https://spacy.io/api/span#has_vector
        """
        if "has_vector" in self.doc.user_span_hooks:
            return self.doc.user_span_hooks["has_vector"](self)
        elif self.vocab.vectors.data.size > 0:
            return any(token.has_vector for token in self)
        elif self.doc.tensor.size > 0:
            return True
        else:
            return False

    @property
    def vector(self):
        """A real-valued meaning representation. Defaults to an average of the
        token vectors.

        RETURNS (numpy.ndarray[ndim=1, dtype='float32']): A 1D numpy array
            representing the span's semantics.

        DOCS: https://spacy.io/api/span#vector
        """
        if "vector" in self.doc.user_span_hooks:
            return self.doc.user_span_hooks["vector"](self)
        if self._vector is None:
            self._vector = sum(t.vector for t in self) / len(self)
        return self._vector

    @property
    def vector_norm(self):
        """The L2 norm of the span's vector representation.

        RETURNS (float): The L2 norm of the vector representation.

        DOCS: https://spacy.io/api/span#vector_norm
        """
        if "vector_norm" in self.doc.user_span_hooks:
            return self.doc.user_span_hooks["vector"](self)
        vector = self.vector
        xp = get_array_module(vector)
        if self._vector_norm is None:
            total = (vector*vector).sum()
            self._vector_norm = xp.sqrt(total) if total != 0. else 0.
        return self._vector_norm

    @property
    def sentiment(self):
        """RETURNS (float): A scalar value indicating the positivity or
            negativity of the span.
        """
        if "sentiment" in self.doc.user_span_hooks:
            return self.doc.user_span_hooks["sentiment"](self)
        else:
            return sum([token.sentiment for token in self]) / len(self)

    @property
    def text(self):
        """RETURNS (unicode): The original verbatim text of the span."""
        text = self.text_with_ws
        if self[-1].whitespace_:
            text = text[:-1]
        return text

    @property
    def text_with_ws(self):
        """The text content of the span with a trailing whitespace character if
        the last token has one.

        RETURNS (unicode): The text content of the span (with trailing
            whitespace).
        """
        return "".join([t.text_with_ws for t in self])

    @property
    def noun_chunks(self):
        """Yields base noun-phrase `Span` objects, if the document has been
        syntactically parsed. A base noun phrase, or "NP chunk", is a noun
        phrase that does not permit other NPs to be nested within it – so no
        NP-level coordination, no prepositional phrases, and no relative
        clauses.

        YIELDS (Span): Base noun-phrase `Span` objects.

        DOCS: https://spacy.io/api/span#noun_chunks
        """
        if not self.doc.is_parsed:
            raise ValueError(Errors.E029)
        # Accumulate the result before beginning to iterate over it. This
        # prevents the tokenisation from being changed out from under us
        # during the iteration. The tricky thing here is that Span accepts
        # its tokenisation changing, so it's okay once we have the Span
        # objects. See Issue #375
        spans = []
        cdef attr_t label
        if self.doc.noun_chunks_iterator is not None:
            for start, end, label in self.doc.noun_chunks_iterator(self):
                spans.append(Span(self.doc, start, end, label=label))
        for span in spans:
            yield span

    @property
    def root(self):
        """The token with the shortest path to the root of the
        sentence (or the root itself). If multiple tokens are equally
        high in the tree, the first token is taken.

        RETURNS (Token): The root token.

        DOCS: https://spacy.io/api/span#root
        """
        self._recalculate_indices()
        if "root" in self.doc.user_span_hooks:
            return self.doc.user_span_hooks["root"](self)
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
        # algorithmically clever, but I think should be quite fast,
        # especially for short spans.
        # For each word, we count the path length, and arg min this measure.
        # We could use better tree logic to save steps here...But I
        # think this should be okay.
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

    @property
    def conjuncts(self):
        """Tokens that are conjoined to the span's root.

        RETURNS (tuple): A tuple of Token objects.

        DOCS: https://spacy.io/api/span#lefts
        """
        return self.root.conjuncts

    @property
    def lefts(self):
        """Tokens that are to the left of the span, whose head is within the
        `Span`.

        YIELDS (Token):A left-child of a token of the span.

        DOCS: https://spacy.io/api/span#lefts
        """
        for token in reversed(self):  # Reverse, so we get tokens in order
            for left in token.lefts:
                if left.i < self.start:
                    yield left

    @property
    def rights(self):
        """Tokens that are to the right of the Span, whose head is within the
        `Span`.

        YIELDS (Token): A right-child of a token of the span.

        DOCS: https://spacy.io/api/span#rights
        """
        for token in self:
            for right in token.rights:
                if right.i >= self.end:
                    yield right

    @property
    def n_lefts(self):
        """The number of tokens that are to the left of the span, whose
        heads are within the span.

        RETURNS (int): The number of leftward immediate children of the
            span, in the syntactic dependency parse.

        DOCS: https://spacy.io/api/span#n_lefts
        """
        return len(list(self.lefts))

    @property
    def n_rights(self):
        """The number of tokens that are to the right of the span, whose
        heads are within the span.

        RETURNS (int): The number of rightward immediate children of the
            span, in the syntactic dependency parse.

        DOCS: https://spacy.io/api/span#n_rights
        """
        return len(list(self.rights))

    @property
    def subtree(self):
        """Tokens within the span and tokens which descend from them.

        YIELDS (Token): A token within the span, or a descendant from it.

        DOCS: https://spacy.io/api/span#subtree
        """
        for word in self.lefts:
            yield from word.subtree
        yield from self
        for word in self.rights:
            yield from word.subtree

    property ent_id:
        """RETURNS (uint64): The entity ID."""
        def __get__(self):
            return self.root.ent_id

        def __set__(self, hash_t key):
            raise NotImplementedError(TempErrors.T007.format(attr="ent_id"))

    property ent_id_:
        """RETURNS (unicode): The (string) entity ID."""
        def __get__(self):
            return self.root.ent_id_

        def __set__(self, hash_t key):
            raise NotImplementedError(TempErrors.T007.format(attr="ent_id_"))

    @property
    def orth_(self):
        """Verbatim text content (identical to `Span.text`). Exists mostly for
        consistency with other attributes.

        RETURNS (unicode): The span's text."""
        return self.text

    @property
    def lemma_(self):
        """RETURNS (unicode): The span's lemma."""
        return " ".join([t.lemma_ for t in self]).strip()

    @property
    def upper_(self):
        """Deprecated. Use `Span.text.upper()` instead."""
        return "".join([t.text_with_ws.upper() for t in self]).strip()

    @property
    def lower_(self):
        """Deprecated. Use `Span.text.lower()` instead."""
        return "".join([t.text_with_ws.lower() for t in self]).strip()

    @property
    def string(self):
        """Deprecated: Use `Span.text_with_ws` instead."""
        return "".join([t.text_with_ws for t in self])

    property label_:
        """RETURNS (unicode): The span's label."""
        def __get__(self):
            return self.doc.vocab.strings[self.label]

        def __set__(self, unicode label_):
            if not label_:
                label_ = ''
            raise NotImplementedError(Errors.E129.format(start=self.start, end=self.end, label=label_))

    property kb_id_:
        """RETURNS (unicode): The named entity's KB ID."""
        def __get__(self):
            return self.doc.vocab.strings[self.kb_id]

        def __set__(self, unicode kb_id_):
            if not kb_id_:
                kb_id_ = ''
            current_label = self.label_
            if not current_label:
                current_label = ''
            raise NotImplementedError(Errors.E131.format(start=self.start, end=self.end,
                                                         label=current_label, kb_id=kb_id_))


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
            raise RuntimeError(Errors.E039)
    return n
