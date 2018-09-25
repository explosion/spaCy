# coding: utf8
# cython: infer_types=True
# cython: bounds_check=False
# cython: profile=True
from __future__ import unicode_literals

cimport cython
cimport numpy as np
import numpy
import numpy.linalg
import struct
import dill
import msgpack
from thinc.neural.util import get_array_module, copy_array

from libc.string cimport memcpy, memset
from libc.math cimport sqrt

from .span cimport Span
from .token cimport Token
from .span cimport Span
from .token cimport Token
from .printers import parse_tree
from ..lexeme cimport Lexeme, EMPTY_LEXEME
from ..typedefs cimport attr_t, flags_t
from ..attrs import intify_attrs, IDS
from ..attrs cimport attr_id_t
from ..attrs cimport ID, ORTH, NORM, LOWER, SHAPE, PREFIX, SUFFIX, CLUSTER
from ..attrs cimport LENGTH, POS, LEMMA, TAG, DEP, HEAD, SPACY, ENT_IOB
from ..attrs cimport ENT_TYPE, SENT_START
from ..parts_of_speech cimport CCONJ, PUNCT, NOUN, univ_pos_t
from ..util import normalize_slice
from ..compat import is_config, copy_reg, pickle, basestring_
from ..errors import Errors, Warnings, deprecation_warning
from .. import util
from .underscore import Underscore, get_ext_args
from ._retokenize import Retokenizer

DEF PADDING = 5


cdef int bounds_check(int i, int length, int padding) except -1:
    if (i + padding) < 0:
        raise IndexError(Errors.E026.format(i=i, length=length))
    if (i - padding) >= length:
        raise IndexError(Errors.E026.format(i=i, length=length))


cdef attr_t get_token_attr(const TokenC* token, attr_id_t feat_name) nogil:
    if feat_name == LEMMA:
        return token.lemma
    elif feat_name == POS:
        return token.pos
    elif feat_name == TAG:
        return token.tag
    elif feat_name == DEP:
        return token.dep
    elif feat_name == HEAD:
        return token.head
    elif feat_name == SENT_START:
        return token.sent_start
    elif feat_name == SPACY:
        return token.spacy
    elif feat_name == ENT_IOB:
        return token.ent_iob
    elif feat_name == ENT_TYPE:
        return token.ent_type
    else:
        return Lexeme.get_struct_attr(token.lex, feat_name)


def _get_chunker(lang):
    try:
        cls = util.get_lang_class(lang)
    except ImportError:
        return None
    except KeyError:
        return None
    return cls.Defaults.syntax_iterators.get(u'noun_chunks')


cdef class Doc:
    """A sequence of Token objects. Access sentences and named entities, export
    annotations to numpy arrays, losslessly serialize to compressed binary
    strings. The `Doc` object holds an array of `TokenC` structs. The
    Python-level `Token` and `Span` objects are views of this array, i.e.
    they don't own the data themselves.

    EXAMPLE: Construction 1
        >>> doc = nlp(u'Some text')

        Construction 2
        >>> from spacy.tokens import Doc
        >>> doc = Doc(nlp.vocab, words=[u'hello', u'world', u'!'],
                      spaces=[True, False, False])
    """
    @classmethod
    def set_extension(cls, name, **kwargs):
        if cls.has_extension(name) and not kwargs.get('force', False):
            raise ValueError(Errors.E090.format(name=name, obj='Doc'))
        Underscore.doc_extensions[name] = get_ext_args(**kwargs)

    @classmethod
    def get_extension(cls, name):
        return Underscore.doc_extensions.get(name)

    @classmethod
    def has_extension(cls, name):
        return name in Underscore.doc_extensions

    @classmethod
    def remove_extension(cls, name):
        if not cls.has_extension(name):
            raise ValueError(Errors.E046.format(name=name))
        return Underscore.doc_extensions.pop(name)

    def __init__(self, Vocab vocab, words=None, spaces=None, user_data=None,
                 orths_and_spaces=None):
        """Create a Doc object.

        vocab (Vocab): A vocabulary object, which must match any models you
            want to use (e.g. tokenizer, parser, entity recognizer).
        words (list or None): A list of unicode strings to add to the document
            as words. If `None`, defaults to empty list.
        spaces (list or None): A list of boolean values, of the same length as
            words. True means that the word is followed by a space, False means
            it is not. If `None`, defaults to `[True]*len(words)`
        user_data (dict or None): Optional extra data to attach to the Doc.
        RETURNS (Doc): The newly constructed object.
        """
        self.vocab = vocab
        size = 20
        self.mem = Pool()
        # Guarantee self.lex[i-x], for any i >= 0 and x < padding is in bounds
        # However, we need to remember the true starting places, so that we can
        # realloc.
        data_start = <TokenC*>self.mem.alloc(size + (PADDING*2), sizeof(TokenC))
        cdef int i
        for i in range(size + (PADDING*2)):
            data_start[i].lex = &EMPTY_LEXEME
            data_start[i].l_edge = i
            data_start[i].r_edge = i
        self.c = data_start + PADDING
        self.max_length = size
        self.length = 0
        self.is_tagged = False
        self.is_parsed = False
        self.sentiment = 0.0
        self.cats = {}
        self.user_hooks = {}
        self.user_token_hooks = {}
        self.user_span_hooks = {}
        self.tensor = numpy.zeros((0,), dtype='float32')
        self.user_data = {} if user_data is None else user_data
        self._vector = None
        self.noun_chunks_iterator = _get_chunker(self.vocab.lang)
        cdef unicode orth
        cdef bint has_space
        if orths_and_spaces is None and words is not None:
            if spaces is None:
                spaces = [True] * len(words)
            elif len(spaces) != len(words):
                raise ValueError(Errors.E027)
            orths_and_spaces = zip(words, spaces)
        if orths_and_spaces is not None:
            for orth_space in orths_and_spaces:
                if isinstance(orth_space, unicode):
                    orth = orth_space
                    has_space = True
                elif isinstance(orth_space, bytes):
                    raise ValueError(Errors.E028.format(value=orth_space))
                else:
                    orth, has_space = orth_space
                # Note that we pass self.mem here --- we have ownership, if LexemeC
                # must be created.
                self.push_back(
                    <const LexemeC*>self.vocab.get(self.mem, orth), has_space)
        # Tough to decide on policy for this. Is an empty doc tagged and parsed?
        # There's no information we'd like to add to it, so I guess so?
        if self.length == 0:
            self.is_tagged = True
            self.is_parsed = True

    @property
    def _(self):
        return Underscore(Underscore.doc_extensions, self)

    @property
    def is_sentenced(self):
        # Check if the document has sentence boundaries,
        # i.e at least one tok has the sent_start in (-1, 1)
        if 'sents' in self.user_hooks:
            return True
        if self.is_parsed:
            return True
        for i in range(self.length):
            if self.c[i].sent_start == -1 or self.c[i].sent_start == 1:
                return True
        else:
            return False

    def __getitem__(self, object i):
        """Get a `Token` or `Span` object.

        i (int or tuple) The index of the token, or the slice of the document
            to get.
        RETURNS (Token or Span): The token at `doc[i]]`, or the span at
            `doc[start : end]`.

        EXAMPLE:
            >>> doc[i]
            Get the `Token` object at position `i`, where `i` is an integer.
            Negative indexing is supported, and follows the usual Python
            semantics, i.e. `doc[-2]` is `doc[len(doc) - 2]`.

            >>> doc[start : end]]
            Get a `Span` object, starting at position `start` and ending at
            position `end`, where `start` and `end` are token indices. For
            instance, `doc[2:5]` produces a span consisting of tokens 2, 3 and
            4. Stepped slices (e.g. `doc[start : end : step]`) are not
            supported, as `Span` objects must be contiguous (cannot have gaps).
            You can use negative indices and open-ended ranges, which have
            their normal Python semantics.
        """
        if isinstance(i, slice):
            start, stop = normalize_slice(len(self), i.start, i.stop, i.step)
            return Span(self, start, stop, label=0)

        if i < 0:
            i = self.length + i
        bounds_check(i, self.length, PADDING)
        return Token.cinit(self.vocab, &self.c[i], i, self)

    def __iter__(self):
        """Iterate over `Token`  objects, from which the annotations can be
        easily accessed. This is the main way of accessing `Token` objects,
        which are the main way annotations are accessed from Python. If faster-
        than-Python speeds are required, you can instead access the annotations
        as a numpy array, or access the underlying C data directly from Cython.

        EXAMPLE:
            >>> for token in doc
        """
        cdef int i
        for i in range(self.length):
            yield Token.cinit(self.vocab, &self.c[i], i, self)

    def __len__(self):
        """The number of tokens in the document.

        RETURNS (int): The number of tokens in the document.

        EXAMPLE:
            >>> len(doc)
        """
        return self.length

    def __unicode__(self):
        return u''.join([t.text_with_ws for t in self])

    def __bytes__(self):
        return u''.join([t.text_with_ws for t in self]).encode('utf-8')

    def __str__(self):
        if is_config(python3=True):
            return self.__unicode__()
        return self.__bytes__()

    def __repr__(self):
        return self.__str__()

    @property
    def doc(self):
        return self

    def char_span(self, int start_idx, int end_idx, label=0, vector=None):
        """Create a `Span` object from the slice `doc.text[start : end]`.

        doc (Doc): The parent document.
        start (int): The index of the first character of the span.
        end (int): The index of the first character after the span.
        label (uint64 or string): A label to attach to the Span, e.g. for
            named entities.
        vector (ndarray[ndim=1, dtype='float32']): A meaning representation of
            the span.
        RETURNS (Span): The newly constructed object.
        """
        if not isinstance(label, int):
            label = self.vocab.strings.add(label)
        cdef int start = token_by_start(self.c, self.length, start_idx)
        if start == -1:
            return None
        cdef int end = token_by_end(self.c, self.length, end_idx)
        if end == -1:
            return None
        # Currently we have the token index, we want the range-end index
        end += 1
        cdef Span span = Span(self, start, end, label=label, vector=vector)
        return span

    def similarity(self, other):
        """Make a semantic similarity estimate. The default estimate is cosine
        similarity using an average of word vectors.

        other (object): The object to compare with. By default, accepts `Doc`,
            `Span`, `Token` and `Lexeme` objects.
        RETURNS (float): A scalar similarity score. Higher is more similar.
        """
        if 'similarity' in self.user_hooks:
            return self.user_hooks['similarity'](self, other)
        if isinstance(other, (Lexeme, Token)) and self.length == 1:
            if self.c[0].lex.orth == other.orth:
                return 1.0
        elif isinstance(other, (Span, Doc)):
            if len(self) == len(other):
                for i in range(self.length):
                    if self[i].orth != other[i].orth:
                        break
                else:
                    return 1.0

        if self.vector_norm == 0 or other.vector_norm == 0:
            return 0.0
        return numpy.dot(self.vector, other.vector) / (self.vector_norm * other.vector_norm)

    property has_vector:
        """A boolean value indicating whether a word vector is associated with
        the object.

        RETURNS (bool): Whether a word vector is associated with the object.
        """
        def __get__(self):
            if 'has_vector' in self.user_hooks:
                return self.user_hooks['has_vector'](self)
            elif self.vocab.vectors.data.size:
                return True
            elif self.tensor.size:
                return True
            else:
                return False

    property vector:
        """A real-valued meaning representation. Defaults to an average of the
        token vectors.

        RETURNS (numpy.ndarray[ndim=1, dtype='float32']): A 1D numpy array
            representing the document's semantics.
        """
        def __get__(self):
            if 'vector' in self.user_hooks:
                return self.user_hooks['vector'](self)
            if self._vector is not None:
                return self._vector
            elif not len(self):
                self._vector = numpy.zeros((self.vocab.vectors_length,),
                                           dtype='f')
                return self._vector
            elif self.vocab.vectors.data.size > 0:
                vector = numpy.zeros((self.vocab.vectors_length,), dtype='f')
                for token in self.c[:self.length]:
                    vector += self.vocab.get_vector(token.lex.orth)
                self._vector = vector / len(self)
                return self._vector
            elif self.tensor.size > 0:
                self._vector = self.tensor.mean(axis=0)
                return self._vector
            else:
                return numpy.zeros((self.vocab.vectors_length,),
                                   dtype='float32')

        def __set__(self, value):
            self._vector = value

    property vector_norm:
        """The L2 norm of the document's vector representation.

        RETURNS (float): The L2 norm of the vector representation.
        """
        def __get__(self):
            if 'vector_norm' in self.user_hooks:
                return self.user_hooks['vector_norm'](self)
            cdef float value
            cdef double norm = 0
            if self._vector_norm is None:
                norm = 0.0
                for value in self.vector:
                    norm += value * value
                self._vector_norm = sqrt(norm) if norm != 0 else 0
            return self._vector_norm

        def __set__(self, value):
            self._vector_norm = value

    property text:
        """A unicode representation of the document text.

        RETURNS (unicode): The original verbatim text of the document.
        """
        def __get__(self):
            return u''.join(t.text_with_ws for t in self)

    property text_with_ws:
        """An alias of `Doc.text`, provided for duck-type compatibility with
        `Span` and `Token`.

        RETURNS (unicode): The original verbatim text of the document.
        """
        def __get__(self):
            return self.text

    property ents:
        """Iterate over the entities in the document. Yields named-entity
        `Span` objects, if the entity recognizer has been applied to the
        document.

        YIELDS (Span): Entities in the document.

        EXAMPLE: Iterate over the span to get individual Token objects,
            or access the label:

            >>> tokens = nlp(u'Mr. Best flew to New York on Saturday morning.')
            >>> ents = list(tokens.ents)
            >>> assert ents[0].label == 346
            >>> assert ents[0].label_ == 'PERSON'
            >>> assert ents[0].orth_ == 'Best'
            >>> assert ents[0].text == 'Mr. Best'
        """
        def __get__(self):
            cdef int i
            cdef const TokenC* token
            cdef int start = -1
            cdef attr_t label = 0
            output = []
            for i in range(self.length):
                token = &self.c[i]
                if token.ent_iob == 1:
                    if start == -1:
                        seq = ['%s|%s' % (t.text, t.ent_iob_) for t in self[i-5:i+5]]
                        raise ValueError(Errors.E093.format(seq=' '.join(seq)))
                elif token.ent_iob == 2 or token.ent_iob == 0:
                    if start != -1:
                        output.append(Span(self, start, i, label=label))
                    start = -1
                    label = 0
                elif token.ent_iob == 3:
                    if start != -1:
                        output.append(Span(self, start, i, label=label))
                    start = i
                    label = token.ent_type
            if start != -1:
                output.append(Span(self, start, self.length, label=label))
            return tuple(output)

        def __set__(self, ents):
            # TODO:
            # 1. Allow negative matches
            # 2. Ensure pre-set NERs are not over-written during statistical
            #    prediction
            # 3. Test basic data-driven ORTH gazetteer
            # 4. Test more nuanced date and currency regex
            cdef int i
            for i in range(self.length):
                self.c[i].ent_type = 0
                self.c[i].ent_iob = 0  # Means missing.
            cdef attr_t ent_type
            cdef int start, end
            for ent_info in ents:
                if isinstance(ent_info, Span):
                    ent_id = ent_info.ent_id
                    ent_type = ent_info.label
                    start = ent_info.start
                    end = ent_info.end
                elif len(ent_info) == 3:
                    ent_type, start, end = ent_info
                else:
                    ent_id, ent_type, start, end = ent_info
                if ent_type is None or ent_type < 0:
                    # Mark as O
                    for i in range(start, end):
                        self.c[i].ent_type = 0
                        self.c[i].ent_iob = 2
                else:
                    # Mark (inside) as I
                    for i in range(start, end):
                        self.c[i].ent_type = ent_type
                        self.c[i].ent_iob = 1
                    # Set start as B
                    self.c[start].ent_iob = 3

    property noun_chunks:
        """Iterate over the base noun phrases in the document. Yields base
        noun-phrase #[code Span] objects, if the document has been
        syntactically parsed. A base noun phrase, or "NP chunk", is a noun
        phrase that does not permit other NPs to be nested within it – so no
        NP-level coordination, no prepositional phrases, and no relative
        clauses.

        YIELDS (Span): Noun chunks in the document.
        """
        def __get__(self):
            if not self.is_parsed:
                raise ValueError(Errors.E029)
            # Accumulate the result before beginning to iterate over it. This
            # prevents the tokenisation from being changed out from under us
            # during the iteration. The tricky thing here is that Span accepts
            # its tokenisation changing, so it's okay once we have the Span
            # objects. See Issue #375.
            spans = []
            if self.noun_chunks_iterator is not None:
                for start, end, label in self.noun_chunks_iterator(self):
                    spans.append(Span(self, start, end, label=label))
            for span in spans:
                yield span

    property sents:
        """Iterate over the sentences in the document. Yields sentence `Span`
        objects. Sentence spans have no label. To improve accuracy on informal
        texts, spaCy calculates sentence boundaries from the syntactic
        dependency parse. If the parser is disabled, the `sents` iterator will
        be unavailable.

        EXAMPLE:
            >>> doc = nlp("This is a sentence. Here's another...")
            >>> assert [s.root.text for s in doc.sents] == ["is", "'s"]
        """
        def __get__(self):
            if not self.is_sentenced:
                raise ValueError(Errors.E030)
            if 'sents' in self.user_hooks:
                yield from self.user_hooks['sents'](self)
            else:
                start = 0
                for i in range(1, self.length):
                    if self.c[i].sent_start == 1:
                        yield Span(self, start, i)
                        start = i
                if start != self.length:
                    yield Span(self, start, self.length)

    cdef int push_back(self, LexemeOrToken lex_or_tok, bint has_space) except -1:
        if self.length == 0:
            # Flip these to false when we see the first token.
            self.is_tagged = False
            self.is_parsed = False
        if self.length == self.max_length:
            self._realloc(self.length * 2)
        cdef TokenC* t = &self.c[self.length]
        if LexemeOrToken is const_TokenC_ptr:
            t[0] = lex_or_tok[0]
        else:
            t.lex = lex_or_tok
        if self.length == 0:
            t.idx = 0
        else:
            t.idx = (t-1).idx + (t-1).lex.length + (t-1).spacy
        t.l_edge = self.length
        t.r_edge = self.length
        if t.lex.orth == 0:
            raise ValueError(Errors.E031.format(i=self.length))
        t.spacy = has_space
        self.length += 1
        return t.idx + t.lex.length + t.spacy

    @cython.boundscheck(False)
    cpdef np.ndarray to_array(self, object py_attr_ids):
        """Export given token attributes to a numpy `ndarray`.
        If `attr_ids` is a sequence of M attributes, the output array will be
        of shape `(N, M)`, where N is the length of the `Doc` (in tokens). If
        `attr_ids` is a single attribute, the output shape will be (N,). You
        can specify attributes by integer ID (e.g. spacy.attrs.LEMMA) or
        string name (e.g. 'LEMMA' or 'lemma').

        attr_ids (list[]): A list of attributes (int IDs or string names).
        RETURNS (numpy.ndarray[long, ndim=2]): A feature matrix, with one row
            per word, and one column per attribute indicated in the input
            `attr_ids`.

        EXAMPLE:
            >>> from spacy.attrs import LOWER, POS, ENT_TYPE, IS_ALPHA
            >>> doc = nlp(text)
            >>> # All strings mapped to integers, for easy export to numpy
            >>> np_array = doc.to_array([LOWER, POS, ENT_TYPE, IS_ALPHA])
        """
        cdef int i, j
        cdef attr_id_t feature
        cdef np.ndarray[attr_t, ndim=2] output
        # Handle scalar/list inputs of strings/ints for py_attr_ids
        if not hasattr(py_attr_ids, '__iter__') \
        and not isinstance(py_attr_ids, basestring_):
            py_attr_ids = [py_attr_ids]

        # Allow strings, e.g. 'lemma' or 'LEMMA'
        py_attr_ids = [(IDS[id_.upper()] if hasattr(id_, 'upper') else id_)
                       for id_ in py_attr_ids]
        # Make an array from the attributes --- otherwise our inner loop is
        # Python dict iteration.
        cdef np.ndarray attr_ids = numpy.asarray(py_attr_ids, dtype='i')
        output = numpy.ndarray(shape=(self.length, len(attr_ids)),
                               dtype=numpy.uint64)
        c_output = <attr_t*>output.data
        c_attr_ids = <attr_id_t*>attr_ids.data
        cdef TokenC* token
        cdef int nr_attr = attr_ids.shape[0]
        for i in range(self.length):
            token = &self.c[i]
            for j in range(nr_attr):
                c_output[i*nr_attr + j] = get_token_attr(token, c_attr_ids[j])
        # Handle 1d case
        return output if len(attr_ids) >= 2 else output.reshape((self.length,))

    def count_by(self, attr_id_t attr_id, exclude=None,
                 PreshCounter counts=None):
        """Count the frequencies of a given attribute. Produces a dict of
        `{attribute (int): count (ints)}` frequencies, keyed by the values of
        the given attribute ID.

        attr_id (int): The attribute ID to key the counts.
        RETURNS (dict): A dictionary mapping attributes to integer counts.

        EXAMPLE:
            >>> from spacy import attrs
            >>> doc = nlp(u'apple apple orange banana')
            >>> tokens.count_by(attrs.ORTH)
            {12800L: 1, 11880L: 2, 7561L: 1}
            >>> tokens.to_array([attrs.ORTH])
            array([[11880], [11880], [7561], [12800]])
        """
        cdef int i
        cdef attr_t attr
        cdef size_t count

        if counts is None:
            counts = PreshCounter()
            output_dict = True
        else:
            output_dict = False
        # Take this check out of the loop, for a bit of extra speed
        if exclude is None:
            for i in range(self.length):
                counts.inc(get_token_attr(&self.c[i], attr_id), 1)
        else:
            for i in range(self.length):
                if not exclude(self[i]):
                    attr = get_token_attr(&self.c[i], attr_id)
                    counts.inc(attr, 1)
        if output_dict:
            return dict(counts)

    def _realloc(self, new_size):
        self.max_length = new_size
        n = new_size + (PADDING * 2)
        # What we're storing is a "padded" array. We've jumped forward PADDING
        # places, and are storing the pointer to that. This way, we can access
        # words out-of-bounds, and get out-of-bounds markers.
        # Now that we want to realloc, we need the address of the true start,
        # so we jump the pointer back PADDING places.
        cdef TokenC* data_start = self.c - PADDING
        data_start = <TokenC*>self.mem.realloc(data_start, n * sizeof(TokenC))
        self.c = data_start + PADDING
        cdef int i
        for i in range(self.length, self.max_length + PADDING):
            self.c[i].lex = &EMPTY_LEXEME

    cdef void set_parse(self, const TokenC* parsed) nogil:
        # TODO: This method is fairly misleading atm. It's used by Parser
        # to actually apply the parse calculated. Need to rethink this.

        # Probably we should use from_array?
        self.is_parsed = True
        for i in range(self.length):
            self.c[i] = parsed[i]

    def from_array(self, attrs, array):
        if SENT_START in attrs and HEAD in attrs:
            raise ValueError(Errors.E032)
        cdef int i, col
        cdef attr_id_t attr_id
        cdef TokenC* tokens = self.c
        cdef int length = len(array)
        # Get set up for fast loading
        cdef Pool mem = Pool()
        cdef int n_attrs = len(attrs)
        attr_ids = <attr_id_t*>mem.alloc(n_attrs, sizeof(attr_id_t))
        for i, attr_id in enumerate(attrs):
            attr_ids[i] = attr_id
        # Now load the data
        for i in range(self.length):
            token = &self.c[i]
            for j in range(n_attrs):
                Token.set_struct_attr(token, attr_ids[j], array[i, j])
        # Auxiliary loading logic
        for col, attr_id in enumerate(attrs):
            if attr_id == TAG:
                for i in range(length):
                    if array[i, col] != 0:
                        self.vocab.morphology.assign_tag(&tokens[i], array[i, col])
        # set flags
        self.is_parsed = bool(HEAD in attrs or DEP in attrs)
        self.is_tagged = bool(TAG in attrs or POS in attrs)
        # if document is parsed, set children
        if self.is_parsed:
            set_children_from_heads(self.c, self.length)
        return self

    def get_lca_matrix(self):
        """Calculates the lowest common ancestor matrix for a given `Doc`.
        Returns LCA matrix containing the integer index of the ancestor, or -1
        if no common ancestor is found (ex if span excludes a necessary
        ancestor). Apologies about the recursion, but the impact on
        performance is negligible given the natural limitations on the depth
        of a typical human sentence.
        """
        # Efficiency notes:
        # We can easily improve the performance here by iterating in Cython.
        # To loop over the tokens in Cython, the easiest way is:
        # for token in doc.c[:doc.c.length]:
        #     head = token + token.head
        # Both token and head will be TokenC* here. The token.head attribute
        # is an integer offset.
        def __pairwise_lca(token_j, token_k, lca_matrix):
            if lca_matrix[token_j.i][token_k.i] != -2:
                return lca_matrix[token_j.i][token_k.i]
            elif token_j == token_k:
                lca_index = token_j.i
            elif token_k.head == token_j:
                lca_index = token_j.i
            elif token_j.head == token_k:
                lca_index = token_k.i
            elif (token_j.head == token_j) and (token_k.head == token_k):
                lca_index = -1
            else:
                lca_index = __pairwise_lca(token_j.head, token_k.head,
                                           lca_matrix)
            lca_matrix[token_j.i][token_k.i] = lca_index
            lca_matrix[token_k.i][token_j.i] = lca_index

            return lca_index

        lca_matrix = numpy.empty((len(self), len(self)), dtype=numpy.int32)
        lca_matrix.fill(-2)
        for j in range(len(self)):
            token_j = self[j]
            for k in range(j, len(self)):
                token_k = self[k]
                lca_matrix[j][k] = __pairwise_lca(token_j, token_k, lca_matrix)
                lca_matrix[k][j] = lca_matrix[j][k]
        return lca_matrix

    def to_disk(self, path, **exclude):
        """Save the current state to a directory.

        path (unicode or Path): A path to a directory, which will be created if
            it doesn't exist. Paths may be either strings or Path-like objects.
        """
        path = util.ensure_path(path)
        with path.open('wb') as file_:
            file_.write(self.to_bytes(**exclude))

    def from_disk(self, path, **exclude):
        """Loads state from a directory. Modifies the object in place and
        returns it.

        path (unicode or Path): A path to a directory. Paths may be either
            strings or `Path`-like objects.
        RETURNS (Doc): The modified `Doc` object.
        """
        path = util.ensure_path(path)
        with path.open('rb') as file_:
            bytes_data = file_.read()
        return self.from_bytes(bytes_data, **exclude)

    def to_bytes(self, **exclude):
        """Serialize, i.e. export the document contents to a binary string.

        RETURNS (bytes): A losslessly serialized copy of the `Doc`, including
            all annotations.
        """
        array_head = [LENGTH, SPACY, LEMMA, ENT_IOB, ENT_TYPE]

        if self.is_tagged:
            array_head.append(TAG)
        # if doc parsed add head and dep attribute
        if self.is_parsed:
            array_head.extend([HEAD, DEP])
        # otherwise add sent_start
        else:
            array_head.append(SENT_START)
        # Msgpack doesn't distinguish between lists and tuples, which is
        # vexing for user data. As a best guess, we *know* that within
        # keys, we must have tuples. In values we just have to hope
        # users don't mind getting a list instead of a tuple.
        serializers = {
            'text': lambda: self.text,
            'array_head': lambda: array_head,
            'array_body': lambda: self.to_array(array_head),
            'sentiment': lambda: self.sentiment,
            'tensor': lambda: self.tensor,
        }
        if 'user_data' not in exclude and self.user_data:
            user_data_keys, user_data_values = list(zip(*self.user_data.items()))
            serializers['user_data_keys'] = lambda: msgpack.dumps(user_data_keys)
            serializers['user_data_values'] = lambda: msgpack.dumps(user_data_values)

        return util.to_bytes(serializers, exclude)

    def from_bytes(self, bytes_data, **exclude):
        """Deserialize, i.e. import the document contents from a binary string.

        data (bytes): The string to load from.
        RETURNS (Doc): Itself.
        """
        if self.length != 0:
            raise ValueError(Errors.E033.format(length=self.length))
        deserializers = {
            'text': lambda b: None,
            'array_head': lambda b: None,
            'array_body': lambda b: None,
            'sentiment': lambda b: None,
            'tensor': lambda b: None,
            'user_data_keys': lambda b: None,
            'user_data_values': lambda b: None,
        }

        msg = util.from_bytes(bytes_data, deserializers, exclude)
        # Msgpack doesn't distinguish between lists and tuples, which is
        # vexing for user data. As a best guess, we *know* that within
        # keys, we must have tuples. In values we just have to hope
        # users don't mind getting a list instead of a tuple.
        if 'user_data' not in exclude and 'user_data_keys' in msg:
            user_data_keys = msgpack.loads(msg['user_data_keys'],
                                           use_list=False, raw=False)
            user_data_values = msgpack.loads(msg['user_data_values'], raw=False)
            for key, value in zip(user_data_keys, user_data_values):
                self.user_data[key] = value

        cdef int i, start, end, has_space

        if 'sentiment' not in exclude and 'sentiment' in msg:
            self.sentiment = msg['sentiment']
        if 'tensor' not in exclude and 'tensor' in msg:
            self.tensor = msg['tensor']

        start = 0
        cdef const LexemeC* lex
        cdef unicode orth_
        text = msg['text']
        attrs = msg['array_body']
        for i in range(attrs.shape[0]):
            end = start + attrs[i, 0]
            has_space = attrs[i, 1]
            orth_ = text[start:end]
            lex = self.vocab.get(self.mem, orth_)
            self.push_back(lex, has_space)
            start = end + has_space
        self.from_array(msg['array_head'][2:], attrs[:, 2:])
        return self

    def extend_tensor(self, tensor):
        '''Concatenate a new tensor onto the doc.tensor object.

        The doc.tensor attribute holds dense feature vectors
        computed by the models in the pipeline. Let's say a
        document with 30 words has a tensor with 128 dimensions
        per word. doc.tensor.shape will be (30, 128). After
        calling doc.extend_tensor with an array of shape (30, 64),
        doc.tensor == (30, 192).
        '''
        xp = get_array_module(self.tensor)
        if self.tensor.size == 0:
            self.tensor.resize(tensor.shape, refcheck=False)
            copy_array(self.tensor, tensor)
        else:
            self.tensor = xp.hstack((self.tensor, tensor))

    def retokenize(self):
        '''Context manager to handle retokenization of the Doc.
        Modifications to the Doc's tokenization are stored, and then
        made all at once when the context manager exits. This is
        much more efficient, and less error-prone.

        All views of the Doc (Span and Token) created before the
        retokenization are invalidated, although they may accidentally
        continue to work.
        '''
        return Retokenizer(self)

    def _bulk_merge(self, spans, attributes):
        """Retokenize the document, such that the spans given as arguments
         are merged into single tokens. The spans need to be in document
         order, and no span intersection is allowed.

        spans (Span[]): Spans to merge, in document order, with all span
            intersections empty. Cannot be emty.
        attributes (Dictionary[]): Attributes to assign to the merged tokens. By default,
            must be the same lenghth as spans, emty dictionaries are allowed.
            attributes are inherited from the syntactic root of the span.
        RETURNS (Token): The first newly merged token.
        """
        cdef unicode tag, lemma, ent_type

        assert len(attributes) == len(spans), "attribute length should be equal to span length" + str(len(attributes)) +\
                                              str(len(spans))
        with self.retokenize() as retokenizer:
            for i, span in enumerate(spans):
                fix_attributes(self, attributes[i])
                remove_label_if_necessary(attributes[i])
                retokenizer.merge(span, attributes[i])

    def merge(self, int start_idx, int end_idx, *args, **attributes):
        """Retokenize the document, such that the span at
        `doc.text[start_idx : end_idx]` is merged into a single token. If
        `start_idx` and `end_idx `do not mark start and end token boundaries,
        the document remains unchanged.

        start_idx (int): Character index of the start of the slice to merge.
        end_idx (int): Character index after the end of the slice to merge.
        **attributes: Attributes to assign to the merged token. By default,
            attributes are inherited from the syntactic root of the span.
        RETURNS (Token): The newly merged token, or `None` if the start and end
            indices did not fall at token boundaries.
        """
        cdef unicode tag, lemma, ent_type
        if len(args) == 3:
            deprecation_warning(Warnings.W003)
            tag, lemma, ent_type = args
            attributes[TAG] = tag
            attributes[LEMMA] = lemma
            attributes[ENT_TYPE] = ent_type
        elif not args:
            fix_attributes(self, attributes)
        elif args:
            raise ValueError(Errors.E034.format(n_args=len(args),
                                                args=repr(args),
                                                kwargs=repr(attributes)))
        remove_label_if_necessary(attributes)

        attributes = intify_attrs(attributes, strings_map=self.vocab.strings)

        cdef int start = token_by_start(self.c, self.length, start_idx)
        if start == -1:
            return None
        cdef int end = token_by_end(self.c, self.length, end_idx)
        if end == -1:
            return None
        # Currently we have the token index, we want the range-end index
        end += 1
        with self.retokenize() as retokenizer:
            retokenizer.merge(self[start:end], attrs=attributes)
        return self[start]

    def print_tree(self, light=False, flat=False):
        """Returns the parse trees in JSON (dict) format.

        light (bool): Don't include lemmas or entities.
        flat (bool): Don't include arcs or modifiers.
        RETURNS (dict): Parse tree as dict.

        EXAMPLE:
            >>> doc = nlp('Bob brought Alice the pizza. Alice ate the pizza.')
            >>> trees = doc.print_tree()
            >>> trees[1]
            {'modifiers': [
                {'modifiers': [], 'NE': 'PERSON', 'word': 'Alice',
                'arc': 'nsubj', 'POS_coarse': 'PROPN', 'POS_fine': 'NNP',
                'lemma': 'Alice'},
                {'modifiers': [
                    {'modifiers': [], 'NE': '', 'word': 'the', 'arc': 'det',
                    'POS_coarse': 'DET', 'POS_fine': 'DT', 'lemma': 'the'}],
                'NE': '', 'word': 'pizza', 'arc': 'dobj', 'POS_coarse': 'NOUN',
                'POS_fine': 'NN', 'lemma': 'pizza'},
                {'modifiers': [], 'NE': '', 'word': '.', 'arc': 'punct',
                'POS_coarse': 'PUNCT', 'POS_fine': '.', 'lemma': '.'}],
                'NE': '', 'word': 'ate', 'arc': 'ROOT', 'POS_coarse': 'VERB',
                'POS_fine': 'VBD', 'lemma': 'eat'}
        """
        return parse_tree(self, light=light, flat=flat)


cdef int token_by_start(const TokenC* tokens, int length, int start_char) except -2:
    cdef int i
    for i in range(length):
        if tokens[i].idx == start_char:
            return i
    else:
        return -1


cdef int token_by_end(const TokenC* tokens, int length, int end_char) except -2:
    cdef int i
    for i in range(length):
        if tokens[i].idx + tokens[i].lex.length == end_char:
            return i
    else:
        return -1


cdef int set_children_from_heads(TokenC* tokens, int length) except -1:
    cdef TokenC* head
    cdef TokenC* child
    cdef int i
    # Set number of left/right children to 0. We'll increment it in the loops.
    for i in range(length):
        tokens[i].l_kids = 0
        tokens[i].r_kids = 0
        tokens[i].l_edge = i
        tokens[i].r_edge = i
    # Set left edges
    for i in range(length):
        child = &tokens[i]
        head = &tokens[i + child.head]
        if child < head:
            head.l_kids += 1
        if child.l_edge < head.l_edge:
            head.l_edge = child.l_edge

    # Set right edges --- same as above, but iterate in reverse
    for i in range(length-1, -1, -1):
        child = &tokens[i]
        head = &tokens[i + child.head]
        if child > head:
            head.r_kids += 1
        if child.r_edge > head.r_edge:
            head.r_edge = child.r_edge


    # Set sentence starts
    for i in range(length):
        if tokens[i].head == 0 and tokens[i].dep != 0:
            tokens[tokens[i].l_edge].sent_start = True


def pickle_doc(doc):
    bytes_data = doc.to_bytes(vocab=False, user_data=False)
    hooks_and_data = (doc.user_data, doc.user_hooks, doc.user_span_hooks,
                      doc.user_token_hooks)
    return (unpickle_doc, (doc.vocab, dill.dumps(hooks_and_data), bytes_data))


def unpickle_doc(vocab, hooks_and_data, bytes_data):
    user_data, doc_hooks, span_hooks, token_hooks = dill.loads(hooks_and_data)

    doc = Doc(vocab, user_data=user_data).from_bytes(bytes_data,
                                                     exclude='user_data')
    doc.user_hooks.update(doc_hooks)
    doc.user_span_hooks.update(span_hooks)
    doc.user_token_hooks.update(token_hooks)
    return doc


copy_reg.pickle(Doc, pickle_doc, unpickle_doc)

def remove_label_if_necessary(attributes):
    # More deprecated attribute handling =/
    if 'label' in attributes:
        attributes['ent_type'] = attributes.pop('label')

def fix_attributes(doc, attributes):
    if 'label' in attributes and 'ent_type' not in attributes:
        if isinstance(attributes['label'], int):
            attributes[ENT_TYPE] = attributes['label']
        else:
            attributes[ENT_TYPE] = doc.vocab.strings[attributes['label']]
    if 'ent_type' in attributes:
        attributes[ENT_TYPE] = attributes['ent_type']
