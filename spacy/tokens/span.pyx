from __future__ import unicode_literals

cimport numpy as np
from libc.math cimport sqrt

import numpy
from thinc.api import get_array_module
import warnings
import copy

from .doc cimport token_by_start, token_by_end, get_token_attr, _get_lca_matrix
from ..structs cimport TokenC, LexemeC
from ..typedefs cimport flags_t, attr_t, hash_t
from ..attrs cimport attr_id_t
from ..parts_of_speech cimport univ_pos_t
from ..attrs cimport *
from ..lexeme cimport Lexeme
from ..symbols cimport dep

from ..util import normalize_slice
from ..errors import Errors, Warnings
from .underscore import Underscore, get_ext_args


cdef class Span:
    """A slice from a Doc object.

    DOCS: https://spacy.io/api/span
    """
    @classmethod
    def set_extension(cls, name, **kwargs):
        """Define a custom attribute which becomes available as `Span._`.

        name (str): Name of the attribute to set.
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

        name (str): Name of the extension.
        RETURNS (tuple): A `(default, method, getter, setter)` tuple.

        DOCS: https://spacy.io/api/span#get_extension
        """
        return Underscore.span_extensions.get(name)

    @classmethod
    def has_extension(cls, name):
        """Check whether an extension has been registered.

        name (str): Name of the extension.
        RETURNS (bool): Whether the extension has been registered.

        DOCS: https://spacy.io/api/span#has_extension
        """
        return name in Underscore.span_extensions

    @classmethod
    def remove_extension(cls, name):
        """Remove a previously registered extension.

        name (str): Name of the extension.
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
        label (int or str): A label to attach to the Span, e.g. for named entities.
        vector (ndarray[ndim=1, dtype='float32']): A meaning representation
            of the span.
        vector_norm (float): The L2 norm of the span's vector representation.
        kb_id (uint64): An identifier from a Knowledge Base to capture the meaning of a named entity.

        DOCS: https://spacy.io/api/span#init
        """
        if not (0 <= start <= end <= len(doc)):
            raise IndexError(Errors.E035.format(start=start, end=end, length=len(doc)))
        self.doc = doc
        if isinstance(label, str):
            label = doc.vocab.strings.add(label)
        if isinstance(kb_id, str):
            kb_id = doc.vocab.strings.add(kb_id)
        if label not in doc.vocab.strings:
            raise ValueError(Errors.E084.format(label=label))

        start_char = doc[start].idx if start < doc.length else len(doc.text)
        if start == end:
            end_char = start_char
        else:
            end_char = doc[end - 1].idx + len(doc[end - 1])
        self.c = SpanC(
            label=label,
            kb_id=kb_id,
            start=start,
            end=end,
            start_char=start_char,
            end_char=end_char,
        )
        self._vector = vector
        self._vector_norm = vector_norm

    def __richcmp__(self, Span other, int op):
        if other is None:
            if op == 0 or op == 1 or op == 2:
                return False
            else:
                return True
        # <
        if op == 0:
            return self.c.start_char < other.c.start_char
        # <=
        elif op == 1:
            return self.c.start_char <= other.c.start_char
        # ==
        elif op == 2:
            # Do the cheap comparisons first
            return (
                (self.c.start_char == other.c.start_char) and \
                (self.c.end_char == other.c.end_char) and \
                (self.c.label == other.c.label) and \
                (self.c.kb_id == other.c.kb_id) and \
                (self.doc == other.doc)
            )
        # !=
        elif op == 3:
            # Do the cheap comparisons first
            return not (
                (self.c.start_char == other.c.start_char) and \
                (self.c.end_char == other.c.end_char) and \
                (self.c.label == other.c.label) and \
                (self.c.kb_id == other.c.kb_id) and \
                (self.doc == other.doc)
            )
        # >
        elif op == 4:
            return self.c.start_char > other.c.start_char
        # >=
        elif op == 5:
            return self.c.start_char >= other.c.start_char

    def __hash__(self):
        return hash((self.doc, self.c.start_char, self.c.end_char, self.c.label, self.c.kb_id))

    def __len__(self):
        """Get the number of tokens in the span.

        RETURNS (int): The number of tokens in the span.

        DOCS: https://spacy.io/api/span#len
        """
        if self.c.end < self.c.start:
            return 0
        return self.c.end - self.c.start

    def __repr__(self):
        return self.text

    def __getitem__(self, object i):
        """Get a `Token` or a `Span` object

        i (int or tuple): The index of the token within the span, or slice of
            the span to get.
        RETURNS (Token or Span): The token at `span[i]`.

        DOCS: https://spacy.io/api/span#getitem
        """
        if isinstance(i, slice):
            start, end = normalize_slice(len(self), i.start, i.stop, i.step)
            return Span(self.doc, start + self.start, end + self.start)
        else:
            if i < 0:
                token_i = self.c.end + i
            else:
                token_i = self.c.start + i
            if self.c.start <= token_i < self.c.end:
                return self.doc[token_i]
            else:
                raise IndexError(Errors.E1002)

    def __iter__(self):
        """Iterate over `Token` objects.

        YIELDS (Token): A `Token` object.

        DOCS: https://spacy.io/api/span#iter
        """
        for i in range(self.c.start, self.c.end):
            yield self.doc[i]

    def __reduce__(self):
        raise NotImplementedError(Errors.E112)

    @property
    def _(self):
        """Custom extension attributes registered via `set_extension`."""
        return Underscore(Underscore.span_extensions, self,
                          start=self.c.start_char, end=self.c.end_char)

    def as_doc(self, *, bint copy_user_data=False, array_head=None, array=None):
        """Create a `Doc` object with a copy of the `Span`'s data.

        copy_user_data (bool): Whether or not to copy the original doc's user data.
        array_head (tuple): `Doc` array attrs, can be passed in to speed up computation.
        array (ndarray): `Doc` as array, can be passed in to speed up computation.
        RETURNS (Doc): The `Doc` copy of the span.

        DOCS: https://spacy.io/api/span#as_doc
        """
        words = [t.text for t in self]
        spaces = [bool(t.whitespace_) for t in self]
        cdef Doc doc = Doc(self.doc.vocab, words=words, spaces=spaces)
        if array_head is None:
            array_head = self.doc._get_array_attrs()
        if array is None:
            array = self.doc.to_array(array_head)
        array = array[self.start : self.end]
        self._fix_dep_copy(array_head, array)
        # Fix initial IOB so the entities are valid for doc.ents below.
        if len(array) > 0 and ENT_IOB in array_head:
            ent_iob_col = array_head.index(ENT_IOB)
            if array[0][ent_iob_col] == 1:
                array[0][ent_iob_col] = 3
        doc.from_array(array_head, array)
        # Set partial entities at the beginning or end of the span to have
        # missing entity annotation. Note: the initial partial entity could be
        # detected from the IOB annotation but the final partial entity can't,
        # so detect and remove both in the same way by checking self.ents.
        span_ents = {(ent.start, ent.end) for ent in self.ents}
        doc_ents = doc.ents
        if len(doc_ents) > 0:
            # Remove initial partial ent
            if (doc_ents[0].start + self.start, doc_ents[0].end + self.start) not in span_ents:
                doc.set_ents([], missing=[doc_ents[0]], default="unmodified")
            # Remove final partial ent
            if (doc_ents[-1].start + self.start, doc_ents[-1].end + self.start) not in span_ents:
                doc.set_ents([], missing=[doc_ents[-1]], default="unmodified")
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
        if copy_user_data:
            user_data = {}
            char_offset = self.start_char
            for key, value in self.doc.user_data.items():
                if isinstance(key, tuple) and len(key) == 4 and key[0] == "._.":
                    data_type, name, start, end = key
                    if start is not None or end is not None:
                        start -= char_offset
                        if end is not None:
                            end -= char_offset
                        user_data[(data_type, name, start, end)] = copy.copy(value)
                else:
                    user_data[key] = copy.copy(value)
            doc.user_data = user_data
        return doc

    def _fix_dep_copy(self, attrs, array):
        """ Rewire dependency links to make sure their heads fall into the span
        while still keeping the correct number of sentences. """
        cdef int length = len(array)
        cdef attr_t value
        cdef int i, head_col, ancestor_i
        old_to_new_root = dict()
        if HEAD in attrs:
            head_col = attrs.index(HEAD)
            for i in range(length):
                # if the HEAD refers to a token outside this span, find a more appropriate ancestor
                token = self[i]
                ancestor_i = token.head.i - self.c.start   # span offset
                if ancestor_i not in range(length):
                    if DEP in attrs:
                        array[i, attrs.index(DEP)] = dep

                    # try finding an ancestor within this span
                    ancestors = token.ancestors
                    for ancestor in ancestors:
                        ancestor_i = ancestor.i - self.c.start
                        if ancestor_i in range(length):
                            array[i, head_col] = numpy.int32(ancestor_i - i).astype(numpy.uint64)

                # if there is no appropriate ancestor, define a new artificial root
                value = array[i, head_col]
                if (i+value) not in range(length):
                    new_root = old_to_new_root.get(ancestor_i, None)
                    if new_root is not None:
                        # take the same artificial root as a previous token from the same sentence
                        array[i, head_col] = numpy.int32(new_root - i).astype(numpy.uint64)
                    else:
                        # set this token as the new artificial root
                        array[i, head_col] = 0
                        old_to_new_root[ancestor_i] = i

        return array

    def get_lca_matrix(self):
        """Calculates a matrix of Lowest Common Ancestors (LCA) for a given
        `Span`, where LCA[i, j] is the index of the lowest common ancestor among
        the tokens span[i] and span[j]. If they have no common ancestor within
        the span, LCA[i, j] will be -1.

        RETURNS (np.array[ndim=2, dtype=numpy.int32]): LCA matrix with shape
            (n, n), where n = len(self).

        DOCS: https://spacy.io/api/span#get_lca_matrix
        """
        return numpy.asarray(_get_lca_matrix(self.doc, self.c.start, self.c.end))

    def similarity(self, other):
        """Make a semantic similarity estimate. The default estimate is cosine
        similarity using an average of word vectors.

        other (object): The object to compare with. By default, accepts `Doc`,
            `Span`, `Token` and `Lexeme` objects.
        RETURNS (float): A scalar similarity score. Higher is more similar.

        DOCS: https://spacy.io/api/span#similarity
        """
        if "similarity" in self.doc.user_span_hooks:
            return self.doc.user_span_hooks["similarity"](self, other)
        if len(self) == 1 and hasattr(other, "orth"):
            if self[0].orth == other.orth:
                return 1.0
        elif isinstance(other, (Doc, Span)) and len(self) == len(other):
            similar = True
            for i in range(len(self)):
                if self[i].orth != getattr(other[i], "orth", None):
                    similar = False
                    break
            if similar:
                return 1.0
        if self.vocab.vectors.n_keys == 0:
            warnings.warn(Warnings.W007.format(obj="Span"))
        if self.vector_norm == 0.0 or other.vector_norm == 0.0:
            warnings.warn(Warnings.W008.format(obj="Span"))
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

    @property
    def vocab(self):
        """RETURNS (Vocab): The Span's Doc's vocab."""
        return self.doc.vocab

    @property
    def sent(self):
        """Obtain the sentence that contains this span. If the given span
        crosses sentence boundaries, return only the first sentence
        to which it belongs.

        RETURNS (Span): The sentence span that the span is a part of.
        """
        if "sent" in self.doc.user_span_hooks:
            return self.doc.user_span_hooks["sent"](self)
        # Use `sent_start` token attribute to find sentence boundaries
        cdef int n = 0
        if self.doc.has_annotation("SENT_START"):
            # Find start of the sentence
            start = self.start
            while self.doc.c[start].sent_start != 1 and start > 0:
                start += -1
            # Find end of the sentence - can be within the entity
            end = self.start + 1
            while end < self.doc.length and self.doc.c[end].sent_start != 1:
                end += 1
                n += 1
                if n >= self.doc.length:
                    break
            return self.doc[start:end]
        else:
            raise ValueError(Errors.E030)

    @property
    def ents(self):
        """The named entities in the span. Returns a tuple of named entity
        `Span` objects, if the entity recognizer has been applied.

        RETURNS (tuple): Entities in the span, one `Span` per entity.

        DOCS: https://spacy.io/api/span#ents
        """
        cdef Span ent
        ents = []
        for ent in self.doc.ents:
            if ent.c.start >= self.c.start:
                if ent.c.end <= self.c.end:
                    ents.append(ent)
                else:
                    break
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
            if not len(self):
                xp = get_array_module(self.vocab.vectors.data)
                self._vector = xp.zeros((self.vocab.vectors_length,), dtype="f")
            else:
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
        if self._vector_norm is None:
            vector = self.vector
            total = (vector*vector).sum()
            xp = get_array_module(vector)
            self._vector_norm = xp.sqrt(total) if total != 0. else 0.
        return self._vector_norm

    @property
    def tensor(self):
        """The span's slice of the doc's tensor.

        RETURNS (ndarray[ndim=2, dtype='float32']): A 2D numpy or cupy array
            representing the span's semantics.
        """
        if self.doc.tensor is None:
            return None
        return self.doc.tensor[self.start : self.end]

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
        """RETURNS (str): The original verbatim text of the span."""
        text = self.text_with_ws
        if len(self) > 0 and self[-1].whitespace_:
            text = text[:-1]
        return text

    @property
    def text_with_ws(self):
        """The text content of the span with a trailing whitespace character if
        the last token has one.

        RETURNS (str): The text content of the span (with trailing
            whitespace).
        """
        return "".join([t.text_with_ws for t in self])


    @property
    def noun_chunks(self):
        """Iterate over the base noun phrases in the span. Yields base
        noun-phrase #[code Span] objects, if the language has a noun chunk iterator.
        Raises a NotImplementedError otherwise.

        A base noun phrase, or "NP chunk", is a noun
        phrase that does not permit other NPs to be nested within it – so no
        NP-level coordination, no prepositional phrases, and no relative
        clauses.

        YIELDS (Span): Noun chunks in the span.

        DOCS: https://spacy.io/api/span#noun_chunks
        """
        for span in self.doc.noun_chunks:
            if span.start >= self.start and span.end <= self.end:
                yield span

    @property
    def root(self):
        """The token with the shortest path to the root of the
        sentence (or the root itself). If multiple tokens are equally
        high in the tree, the first token is taken.

        RETURNS (Token): The root token.

        DOCS: https://spacy.io/api/span#root
        """
        if "root" in self.doc.user_span_hooks:
            return self.doc.user_span_hooks["root"](self)
        # This should probably be called 'head', and the other one called
        # 'gov'. But we went with 'head' elsewhere, and now we're stuck =/
        cdef int i
        # First, we scan through the Span, and check whether there's a word
        # with head==0, i.e. a sentence root. If so, we can return it. The
        # longer the span, the more likely it contains a sentence root, and
        # in this case we return in linear time.
        for i in range(self.c.start, self.c.end):
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
        for i in range(self.c.start, self.c.end):
            if self.c.start <= (i+self.doc.c[i].head) < self.c.end:
                continue
            words_to_root = _count_words_to_root(&self.doc.c[i], self.doc.length)
            if words_to_root < current_best:
                current_best = words_to_root
                root = i
        if root == -1:
            return self.doc[self.c.start]
        else:
            return self.doc[root]

    def char_span(self, int start_idx, int end_idx, label=0, kb_id=0, vector=None):
        """Create a `Span` object from the slice `span.text[start : end]`.

        start (int): The index of the first character of the span.
        end (int): The index of the first character after the span.
        label (uint64 or string): A label to attach to the Span, e.g. for
            named entities.
        kb_id (uint64 or string):  An ID from a KB to capture the meaning of a named entity.
        vector (ndarray[ndim=1, dtype='float32']): A meaning representation of
            the span.
        RETURNS (Span): The newly constructed object.
        """
        start_idx += self.c.start_char
        end_idx += self.c.start_char
        return self.doc.char_span(start_idx, end_idx, label=label, kb_id=kb_id, vector=vector)

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

    property start:
        def __get__(self):
            return self.c.start

        def __set__(self, int start):
            if start < 0:
                raise IndexError("TODO")
            self.c.start = start

    property end:
        def __get__(self):
            return self.c.end

        def __set__(self, int end):
            if end < 0:
                raise IndexError("TODO")
            self.c.end = end

    property start_char:
        def __get__(self):
            return self.c.start_char

        def __set__(self, int start_char):
            if start_char < 0:
                raise IndexError("TODO")
            self.c.start_char = start_char

    property end_char:
        def __get__(self):
            return self.c.end_char

        def __set__(self, int end_char):
            if end_char < 0:
                raise IndexError("TODO")
            self.c.end_char = end_char

    property label:
        def __get__(self):
            return self.c.label

        def __set__(self, attr_t label):
            self.c.label = label

    property kb_id:
        def __get__(self):
            return self.c.kb_id

        def __set__(self, attr_t kb_id):
            self.c.kb_id = kb_id

    property ent_id:
        """RETURNS (uint64): The entity ID."""
        def __get__(self):
            return self.root.ent_id

        def __set__(self, hash_t key):
            raise NotImplementedError(Errors.E200.format(attr="ent_id"))

    property ent_id_:
        """RETURNS (str): The (string) entity ID."""
        def __get__(self):
            return self.root.ent_id_

        def __set__(self, unicode key):
            raise NotImplementedError(Errors.E200.format(attr="ent_id_"))

    @property
    def orth_(self):
        """Verbatim text content (identical to `Span.text`). Exists mostly for
        consistency with other attributes.

        RETURNS (str): The span's text."""
        return self.text

    @property
    def lemma_(self):
        """RETURNS (str): The span's lemma."""
        return "".join([t.lemma_ + t.whitespace_ for t in self]).strip()

    property label_:
        """RETURNS (str): The span's label."""
        def __get__(self):
            return self.doc.vocab.strings[self.label]

        def __set__(self, unicode label_):
            self.label = self.doc.vocab.strings.add(label_)

    property kb_id_:
        """RETURNS (str): The named entity's KB ID."""
        def __get__(self):
            return self.doc.vocab.strings[self.kb_id]

        def __set__(self, unicode kb_id_):
            self.kb_id = self.doc.vocab.strings.add(kb_id_)


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
