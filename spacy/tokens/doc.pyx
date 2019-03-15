
# coding: utf8
# cython: infer_types=True
# cython: bounds_check=False
# cython: profile=True
from __future__ import unicode_literals

cimport cython
cimport numpy as np
from libc.string cimport memcpy, memset
from libc.math cimport sqrt

import numpy
import numpy.linalg
import struct
import srsly
from thinc.neural.util import get_array_module, copy_array

from .span cimport Span
from .token cimport Token
from ..lexeme cimport Lexeme, EMPTY_LEXEME
from ..typedefs cimport attr_t, flags_t
from ..attrs cimport ID, ORTH, NORM, LOWER, SHAPE, PREFIX, SUFFIX, CLUSTER
from ..attrs cimport LENGTH, POS, LEMMA, TAG, DEP, HEAD, SPACY, ENT_IOB
from ..attrs cimport ENT_TYPE, SENT_START, attr_id_t
from ..parts_of_speech cimport CCONJ, PUNCT, NOUN, univ_pos_t

from ..attrs import intify_attrs, IDS
from ..util import normalize_slice
from ..compat import is_config, copy_reg, pickle, basestring_
from ..errors import deprecation_warning, models_warning, user_warning
from ..errors import Errors, Warnings
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
    return cls.Defaults.syntax_iterators.get("noun_chunks")


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

    DOCS: https://spacy.io/api/doc
    """

    @classmethod
    def set_extension(cls, name, **kwargs):
        """Define a custom attribute which becomes available as `Doc._`.

        name (unicode): Name of the attribute to set.
        default: Optional default value of the attribute.
        getter (callable): Optional getter function.
        setter (callable): Optional setter function.
        method (callable): Optional method for method extension.
        force (bool): Force overwriting existing attribute.

        DOCS: https://spacy.io/api/doc#set_extension
        USAGE: https://spacy.io/usage/processing-pipelines#custom-components-attributes
        """
        if cls.has_extension(name) and not kwargs.get("force", False):
            raise ValueError(Errors.E090.format(name=name, obj="Doc"))
        Underscore.doc_extensions[name] = get_ext_args(**kwargs)

    @classmethod
    def get_extension(cls, name):
        """Look up a previously registered extension by name.

        name (unicode): Name of the extension.
        RETURNS (tuple): A `(default, method, getter, setter)` tuple.

        DOCS: https://spacy.io/api/doc#get_extension
        """
        return Underscore.doc_extensions.get(name)

    @classmethod
    def has_extension(cls, name):
        """Check whether an extension has been registered.

        name (unicode): Name of the extension.
        RETURNS (bool): Whether the extension has been registered.

        DOCS: https://spacy.io/api/doc#has_extension
        """
        return name in Underscore.doc_extensions

    @classmethod
    def remove_extension(cls, name):
        """Remove a previously registered extension.

        name (unicode): Name of the extension.
        RETURNS (tuple): A `(default, method, getter, setter)` tuple of the
            removed extension.

        DOCS: https://spacy.io/api/doc#remove_extension
        """
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

        DOCS: https://spacy.io/api/doc#init
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
        self.tensor = numpy.zeros((0,), dtype="float32")
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
        """Custom extension attributes registered via `set_extension`."""
        return Underscore(Underscore.doc_extensions, self)

    @property
    def is_sentenced(self):
        """Check if the document has sentence boundaries assigned. This is
        defined as having at least one of the following:

        a) An entry "sents" in doc.user_hooks";
        b) sent.is_parsed is set to True;
        c) At least one token other than the first where sent_start is not None.
        """
        if "sents" in self.user_hooks:
            return True
        if self.is_parsed:
            return True
        for i in range(1, self.length):
            if self.c[i].sent_start == -1 or self.c[i].sent_start == 1:
                return True
        return False

    @property
    def is_nered(self):
        """Check if the document has named entities set. Will return True if
        *any* of the tokens has a named entity tag set (even if the others are
        uknown values).
        """
        for i in range(self.length):
            if self.c[i].ent_iob != 0:
                return True
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

        DOCS: https://spacy.io/api/doc#getitem
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

        DOCS: https://spacy.io/api/doc#iter
        """
        cdef int i
        for i in range(self.length):
            yield Token.cinit(self.vocab, &self.c[i], i, self)

    def __len__(self):
        """The number of tokens in the document.

        RETURNS (int): The number of tokens in the document.

        DOCS: https://spacy.io/api/doc#len
        """
        return self.length

    def __unicode__(self):
        return "".join([t.text_with_ws for t in self])

    def __bytes__(self):
        return "".join([t.text_with_ws for t in self]).encode("utf-8")

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

        DOCS: https://spacy.io/api/doc#char_span
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

        DOCS: https://spacy.io/api/doc#similarity
        """
        if "similarity" in self.user_hooks:
            return self.user_hooks["similarity"](self, other)
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
        if self.vocab.vectors.n_keys == 0:
            models_warning(Warnings.W007.format(obj="Doc"))
        if self.vector_norm == 0 or other.vector_norm == 0:
            user_warning(Warnings.W008.format(obj="Doc"))
            return 0.0
        vector = self.vector
        xp = get_array_module(vector)
        return xp.dot(vector, other.vector) / (self.vector_norm * other.vector_norm)

    @property
    def has_vector(self):
        """A boolean value indicating whether a word vector is associated with
        the object.

        RETURNS (bool): Whether a word vector is associated with the object.

        DOCS: https://spacy.io/api/doc#has_vector
        """
        if "has_vector" in self.user_hooks:
            return self.user_hooks["has_vector"](self)
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

        DOCS: https://spacy.io/api/doc#vector
        """
        def __get__(self):
            if "vector" in self.user_hooks:
                return self.user_hooks["vector"](self)
            if self._vector is not None:
                return self._vector
            elif not len(self):
                self._vector = numpy.zeros((self.vocab.vectors_length,), dtype="f")
                return self._vector
            elif self.vocab.vectors.data.size > 0:
                self._vector = sum(t.vector for t in self) / len(self)
                return self._vector
            elif self.tensor.size > 0:
                self._vector = self.tensor.mean(axis=0)
                return self._vector
            else:
                return numpy.zeros((self.vocab.vectors_length,), dtype="float32")

        def __set__(self, value):
            self._vector = value

    property vector_norm:
        """The L2 norm of the document's vector representation.

        RETURNS (float): The L2 norm of the vector representation.

        DOCS: https://spacy.io/api/doc#vector_norm
        """
        def __get__(self):
            if "vector_norm" in self.user_hooks:
                return self.user_hooks["vector_norm"](self)
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

    @property
    def text(self):
        """A unicode representation of the document text.

        RETURNS (unicode): The original verbatim text of the document.
        """
        return "".join(t.text_with_ws for t in self)

    @property
    def text_with_ws(self):
        """An alias of `Doc.text`, provided for duck-type compatibility with
        `Span` and `Token`.

        RETURNS (unicode): The original verbatim text of the document.
        """
        return self.text

    property ents:
        """The named entities in the document. Returns a tuple of named entity
        `Span` objects, if the entity recognizer has been applied.

        RETURNS (tuple): Entities in the document, one `Span` per entity.

        DOCS: https://spacy.io/api/doc#ents
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
                        seq = ["%s|%s" % (t.text, t.ent_iob_) for t in self[i-5:i+5]]
                        raise ValueError(Errors.E093.format(seq=" ".join(seq)))
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
            tokens_in_ents = {}
            cdef attr_t entity_type
            cdef int ent_start, ent_end
            for ent_info in ents:
                entity_type, ent_start, ent_end = get_entity_info(ent_info)
                for token_index in range(ent_start, ent_end):
                    if token_index in tokens_in_ents.keys():
                        raise ValueError(Errors.E103.format(
                            span1=(tokens_in_ents[token_index][0],
                                   tokens_in_ents[token_index][1],
                                   self.vocab.strings[tokens_in_ents[token_index][2]]),
                            span2=(ent_start, ent_end, self.vocab.strings[entity_type])))
                    tokens_in_ents[token_index] = (ent_start, ent_end, entity_type)
            cdef int i
            for i in range(self.length):
                self.c[i].ent_type = 0
                self.c[i].ent_iob = 0  # Means missing.
            cdef attr_t ent_type
            cdef int start, end
            for ent_info in ents:
                ent_type, start, end = get_entity_info(ent_info)
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

    @property
    def noun_chunks(self):
        """Iterate over the base noun phrases in the document. Yields base
        noun-phrase #[code Span] objects, if the document has been
        syntactically parsed. A base noun phrase, or "NP chunk", is a noun
        phrase that does not permit other NPs to be nested within it – so no
        NP-level coordination, no prepositional phrases, and no relative
        clauses.

        YIELDS (Span): Noun chunks in the document.

        DOCS: https://spacy.io/api/doc#noun_chunks
        """
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

    @property
    def sents(self):
        """Iterate over the sentences in the document. Yields sentence `Span`
        objects. Sentence spans have no label. To improve accuracy on informal
        texts, spaCy calculates sentence boundaries from the syntactic
        dependency parse. If the parser is disabled, the `sents` iterator will
        be unavailable.

        YIELDS (Span): Sentences in the document.

        DOCS: https://spacy.io/api/doc#sents
        """
        if not self.is_sentenced:
            raise ValueError(Errors.E030)
        if "sents" in self.user_hooks:
            yield from self.user_hooks["sents"](self)
        else:
            start = 0
            for i in range(1, self.length):
                if self.c[i].sent_start == 1:
                    yield Span(self, start, i)
                    start = i
            if start != self.length:
                yield Span(self, start, self.length)

    @property
    def lang(self):
        """RETURNS (uint64): ID of the language of the doc's vocabulary."""
        return self.vocab.strings[self.vocab.lang]

    @property
    def lang_(self):
        """RETURNS (unicode): Language of the doc's vocabulary, e.g. 'en'."""
        return self.vocab.lang

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
        if self.length == 1:
            # Set token.sent_start to 1 for first token. See issue #2869
            self.c[0].sent_start = 1
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
        # See also #3064
        if isinstance(py_attr_ids, basestring_):
            # Handle inputs like doc.to_array('ORTH')
            py_attr_ids = [py_attr_ids]
        elif not hasattr(py_attr_ids, "__iter__"):
            # Handle inputs like doc.to_array(ORTH)
            py_attr_ids = [py_attr_ids]
        # Allow strings, e.g. 'lemma' or 'LEMMA'
        py_attr_ids = [(IDS[id_.upper()] if hasattr(id_, "upper") else id_)
                       for id_ in py_attr_ids]
        # Make an array from the attributes --- otherwise our inner loop is
        # Python dict iteration.
        cdef np.ndarray attr_ids = numpy.asarray(py_attr_ids, dtype="i")
        output = numpy.ndarray(shape=(self.length, len(attr_ids)), dtype=numpy.uint64)
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

    def count_by(self, attr_id_t attr_id, exclude=None, PreshCounter counts=None):
        """Count the frequencies of a given attribute. Produces a dict of
        `{attribute (int): count (ints)}` frequencies, keyed by the values of
        the given attribute ID.

        attr_id (int): The attribute ID to key the counts.
        RETURNS (dict): A dictionary mapping attributes to integer counts.

        DOCS: https://spacy.io/api/doc#count_by
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
        """Load attributes from a numpy array. Write to a `Doc` object, from an
        `(M, N)` array of attributes.

        attrs (list) A list of attribute ID ints.
        array (numpy.ndarray[ndim=2, dtype='int32']): The attribute values.
        RETURNS (Doc): Itself.

        DOCS: https://spacy.io/api/doc#from_array
        """
        # Handle scalar/list inputs of strings/ints for py_attr_ids
        # See also #3064
        if isinstance(attrs, basestring_):
            # Handle inputs like doc.to_array('ORTH')
            attrs = [attrs]
        elif not hasattr(attrs, "__iter__"):
            # Handle inputs like doc.to_array(ORTH)
            attrs = [attrs]
        # Allow strings, e.g. 'lemma' or 'LEMMA'
        attrs = [(IDS[id_.upper()] if hasattr(id_, "upper") else id_)
                 for id_ in attrs]

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
        if len(array.shape) == 1:
            array = array.reshape((array.size, 1))
        # Do TAG first. This lets subsequent loop override stuff like POS, LEMMA
        if TAG in attrs:
            col = attrs.index(TAG)
            for i in range(length):
                if array[i, col] != 0:
                    self.vocab.morphology.assign_tag(&tokens[i], array[i, col])
        # Now load the data
        for i in range(self.length):
            token = &self.c[i]
            for j in range(n_attrs):
                if attr_ids[j] != TAG:
                    Token.set_struct_attr(token, attr_ids[j], array[i, j])
        # Set flags
        self.is_parsed = bool(self.is_parsed or HEAD in attrs or DEP in attrs)
        self.is_tagged = bool(self.is_tagged or TAG in attrs or POS in attrs)
        # If document is parsed, set children
        if self.is_parsed:
            set_children_from_heads(self.c, self.length)
        return self

    def get_lca_matrix(self):
        """Calculates a matrix of Lowest Common Ancestors (LCA) for a given
        `Doc`, where LCA[i, j] is the index of the lowest common ancestor among
        token i and j.

        RETURNS (np.array[ndim=2, dtype=numpy.int32]): LCA matrix with shape
            (n, n), where n = len(self).

        DOCS: https://spacy.io/api/doc#get_lca_matrix
        """
        return numpy.asarray(_get_lca_matrix(self, 0, len(self)))

    def to_disk(self, path, **kwargs):
        """Save the current state to a directory.

        path (unicode or Path): A path to a directory, which will be created if
            it doesn't exist. Paths may be either strings or Path-like objects.
        exclude (list): String names of serialization fields to exclude.

        DOCS: https://spacy.io/api/doc#to_disk
        """
        path = util.ensure_path(path)
        with path.open("wb") as file_:
            file_.write(self.to_bytes(**kwargs))

    def from_disk(self, path, **kwargs):
        """Loads state from a directory. Modifies the object in place and
        returns it.

        path (unicode or Path): A path to a directory. Paths may be either
            strings or `Path`-like objects.
        exclude (list): String names of serialization fields to exclude.
        RETURNS (Doc): The modified `Doc` object.

        DOCS: https://spacy.io/api/doc#from_disk
        """
        path = util.ensure_path(path)
        with path.open("rb") as file_:
            bytes_data = file_.read()
        return self.from_bytes(bytes_data, **kwargs)

    def to_bytes(self, exclude=tuple(), **kwargs):
        """Serialize, i.e. export the document contents to a binary string.

        exclude (list): String names of serialization fields to exclude.
        RETURNS (bytes): A losslessly serialized copy of the `Doc`, including
            all annotations.

        DOCS: https://spacy.io/api/doc#to_bytes
        """
        array_head = [LENGTH, SPACY, LEMMA, ENT_IOB, ENT_TYPE]
        if self.is_tagged:
            array_head.append(TAG)
        # If doc parsed add head and dep attribute
        if self.is_parsed:
            array_head.extend([HEAD, DEP])
        # Otherwise add sent_start
        else:
            array_head.append(SENT_START)
        # Msgpack doesn't distinguish between lists and tuples, which is
        # vexing for user data. As a best guess, we *know* that within
        # keys, we must have tuples. In values we just have to hope
        # users don't mind getting a list instead of a tuple.
        serializers = {
            "text": lambda: self.text,
            "array_head": lambda: array_head,
            "array_body": lambda: self.to_array(array_head),
            "sentiment": lambda: self.sentiment,
            "tensor": lambda: self.tensor,
        }
        for key in kwargs:
            if key in serializers or key in ("user_data", "user_data_keys", "user_data_values"):
                raise ValueError(Errors.E128.format(arg=key))
        if "user_data" not in exclude and self.user_data:
            user_data_keys, user_data_values = list(zip(*self.user_data.items()))
            if "user_data_keys" not in exclude:
                serializers["user_data_keys"] = lambda: srsly.msgpack_dumps(user_data_keys)
            if "user_data_values" not in exclude:
                serializers["user_data_values"] = lambda: srsly.msgpack_dumps(user_data_values)
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, bytes_data, exclude=tuple(), **kwargs):
        """Deserialize, i.e. import the document contents from a binary string.

        data (bytes): The string to load from.
        exclude (list): String names of serialization fields to exclude.
        RETURNS (Doc): Itself.

        DOCS: https://spacy.io/api/doc#from_bytes
        """
        if self.length != 0:
            raise ValueError(Errors.E033.format(length=self.length))
        deserializers = {
            "text": lambda b: None,
            "array_head": lambda b: None,
            "array_body": lambda b: None,
            "sentiment": lambda b: None,
            "tensor": lambda b: None,
            "user_data_keys": lambda b: None,
            "user_data_values": lambda b: None,
        }
        for key in kwargs:
            if key in deserializers or key in ("user_data",):
                raise ValueError(Errors.E128.format(arg=key))
        msg = util.from_bytes(bytes_data, deserializers, exclude)
        # Msgpack doesn't distinguish between lists and tuples, which is
        # vexing for user data. As a best guess, we *know* that within
        # keys, we must have tuples. In values we just have to hope
        # users don't mind getting a list instead of a tuple.
        if "user_data" not in exclude and "user_data_keys" in msg:
            user_data_keys = srsly.msgpack_loads(msg["user_data_keys"], use_list=False)
            user_data_values = srsly.msgpack_loads(msg["user_data_values"])
            for key, value in zip(user_data_keys, user_data_values):
                self.user_data[key] = value
        cdef int i, start, end, has_space
        if "sentiment" not in exclude and "sentiment" in msg:
            self.sentiment = msg["sentiment"]
        if "tensor" not in exclude and "tensor" in msg:
            self.tensor = msg["tensor"]
        start = 0
        cdef const LexemeC* lex
        cdef unicode orth_
        text = msg["text"]
        attrs = msg["array_body"]
        for i in range(attrs.shape[0]):
            end = start + attrs[i, 0]
            has_space = attrs[i, 1]
            orth_ = text[start:end]
            lex = self.vocab.get(self.mem, orth_)
            self.push_back(lex, has_space)
            start = end + has_space
        self.from_array(msg["array_head"][2:], attrs[:, 2:])
        return self

    def extend_tensor(self, tensor):
        """Concatenate a new tensor onto the doc.tensor object.

        The doc.tensor attribute holds dense feature vectors
        computed by the models in the pipeline. Let's say a
        document with 30 words has a tensor with 128 dimensions
        per word. doc.tensor.shape will be (30, 128). After
        calling doc.extend_tensor with an array of shape (30, 64),
        doc.tensor == (30, 192).
        """
        xp = get_array_module(self.tensor)
        if self.tensor.size == 0:
            self.tensor.resize(tensor.shape, refcheck=False)
            copy_array(self.tensor, tensor)
        else:
            self.tensor = xp.hstack((self.tensor, tensor))

    def retokenize(self):
        """Context manager to handle retokenization of the Doc.
        Modifications to the Doc's tokenization are stored, and then
        made all at once when the context manager exits. This is
        much more efficient, and less error-prone.

        All views of the Doc (Span and Token) created before the
        retokenization are invalidated, although they may accidentally
        continue to work.

        DOCS: https://spacy.io/api/doc#retokenize
        USAGE: https://spacy.io/usage/linguistic-features#retokenization
        """
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
        attr_len = len(attributes)
        span_len = len(spans)
        if not attr_len == span_len:
            raise ValueError(Errors.E121.format(attr_len=attr_len, span_len=span_len))
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
        deprecation_warning(Warnings.W013.format(obj="Doc"))
        if len(args) == 3:
            deprecation_warning(Warnings.W003)
            tag, lemma, ent_type = args
            attributes[TAG] = tag
            attributes[LEMMA] = lemma
            attributes[ENT_TYPE] = ent_type
        elif not args:
            fix_attributes(self, attributes)
        elif args:
            raise ValueError(Errors.E034.format(n_args=len(args), args=repr(args),
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
        raise ValueError(Errors.E105)

    def to_json(self, underscore=None):
        """Convert a Doc to JSON. The format it produces will be the new format
        for the `spacy train` command (not implemented yet).

        underscore (list): Optional list of string names of custom doc._.
        attributes. Attribute values need to be JSON-serializable. Values will
        be added to an "_" key in the data, e.g. "_": {"foo": "bar"}.
        RETURNS (dict): The data in spaCy's JSON format.

        DOCS: https://spacy.io/api/doc#to_json
        """
        data = {"text": self.text}
        if self.is_nered:
            data["ents"] = [{"start": ent.start_char, "end": ent.end_char,
                            "label": ent.label_} for ent in self.ents]
        if self.is_sentenced:
            sents = list(self.sents)
            data["sents"] = [{"start": sent.start_char, "end": sent.end_char}
                             for sent in sents]
        if self.cats:
            data["cats"] = self.cats
        data["tokens"] = []
        for token in self:
            token_data = {"id": token.i, "start": token.idx, "end": token.idx + len(token)}
            if self.is_tagged:
                token_data["pos"] = token.pos_
                token_data["tag"] = token.tag_
            if self.is_parsed:
                token_data["dep"] = token.dep_
                token_data["head"] = token.head.i
            data["tokens"].append(token_data)
        if underscore:
            data["_"] = {}
            for attr in underscore:
                if not self.has_extension(attr):
                    raise ValueError(Errors.E106.format(attr=attr, opts=underscore))
                value = self._.get(attr)
                if not srsly.is_json_serializable(value):
                    raise ValueError(Errors.E107.format(attr=attr, value=repr(value)))
                data["_"][attr] = value
        return data


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
    # Three times, for non-projectivity. See issue #3170. This isn't a very
    # satisfying fix, but I think it's sufficient.
    for loop_count in range(3):
        # Set left edges
        for i in range(length):
            child = &tokens[i]
            head = &tokens[i + child.head]
            if child < head and loop_count == 0:
                head.l_kids += 1
            if child.l_edge < head.l_edge:
                head.l_edge = child.l_edge
            if child.r_edge > head.r_edge:
                head.r_edge = child.r_edge
        # Set right edges - same as above, but iterate in reverse
        for i in range(length-1, -1, -1):
            child = &tokens[i]
            head = &tokens[i + child.head]
            if child > head and loop_count == 0:
                head.r_kids += 1
            if child.r_edge > head.r_edge:
                head.r_edge = child.r_edge
            if child.l_edge < head.l_edge:
                head.l_edge = child.l_edge
    # Set sentence starts
    for i in range(length):
        if tokens[i].head == 0 and tokens[i].dep != 0:
            tokens[tokens[i].l_edge].sent_start = True


cdef int _get_tokens_lca(Token token_j, Token token_k):
    """Given two tokens, returns the index of the lowest common ancestor
    (LCA) among the two. If they have no common ancestor, -1 is returned.

    token_j (Token): a token.
    token_k (Token): another token.
    RETURNS (int): index of lowest common ancestor, or -1 if the tokens
        have no common ancestor.
    """
    if token_j == token_k:
        return token_j.i
    elif token_j.head == token_k:
        return token_k.i
    elif token_k.head == token_j:
        return token_j.i
    token_j_ancestors = set(token_j.ancestors)
    if token_k in token_j_ancestors:
        return token_k.i
    for token_k_ancestor in token_k.ancestors:
        if token_k_ancestor == token_j:
            return token_j.i
        if token_k_ancestor in token_j_ancestors:
            return token_k_ancestor.i
    return -1


cdef int [:,:] _get_lca_matrix(Doc doc, int start, int end):
    """Given a doc and a start and end position defining a set of contiguous
    tokens within it, returns a matrix of Lowest Common Ancestors (LCA), where
    LCA[i, j] is the index of the lowest common ancestor among token i and j.
    If the tokens have no common ancestor within the specified span,
    LCA[i, j] will be -1.

    doc (Doc): The index of the token, or the slice of the document
    start (int): First token to be included in the LCA matrix.
    end (int): Position of next to last token included in the LCA matrix.
    RETURNS (int [:, :]): memoryview of numpy.array[ndim=2, dtype=numpy.int32],
        with shape (n, n), where n = len(doc).
    """
    cdef int [:,:] lca_matrix
    n_tokens= end - start
    lca_mat = numpy.empty((n_tokens, n_tokens), dtype=numpy.int32)
    lca_mat.fill(-1)
    lca_matrix = lca_mat
    for j in range(n_tokens):
        token_j = doc[start + j]
        # the common ancestor of token and itself is itself:
        lca_matrix[j, j] = j
        # we will only iterate through tokens in the same sentence
        sent = token_j.sent
        sent_start = sent.start
        j_idx_in_sent = start + j - sent_start
        n_missing_tokens_in_sent = len(sent) - j_idx_in_sent
        # make sure we do not go past `end`, in cases where `end` < sent.end
        max_range = min(j + n_missing_tokens_in_sent, end)
        for k in range(j + 1, max_range):
            lca = _get_tokens_lca(token_j, doc[start + k])
            # if lca is outside of span, we set it to -1
            if not start <= lca < end:
                lca_matrix[j, k] = -1
                lca_matrix[k, j] = -1
            else:
                lca_matrix[j, k] = lca - start
                lca_matrix[k, j] = lca - start
    return lca_matrix


def pickle_doc(doc):
    bytes_data = doc.to_bytes(exclude=["vocab", "user_data"])
    hooks_and_data = (doc.user_data, doc.user_hooks, doc.user_span_hooks,
                      doc.user_token_hooks)
    return (unpickle_doc, (doc.vocab, srsly.pickle_dumps(hooks_and_data), bytes_data))


def unpickle_doc(vocab, hooks_and_data, bytes_data):
    user_data, doc_hooks, span_hooks, token_hooks = srsly.pickle_loads(hooks_and_data)

    doc = Doc(vocab, user_data=user_data).from_bytes(bytes_data, exclude=["user_data"])
    doc.user_hooks.update(doc_hooks)
    doc.user_span_hooks.update(span_hooks)
    doc.user_token_hooks.update(token_hooks)
    return doc


copy_reg.pickle(Doc, pickle_doc, unpickle_doc)


def remove_label_if_necessary(attributes):
    # More deprecated attribute handling =/
    if "label" in attributes:
        attributes["ent_type"] = attributes.pop("label")


def fix_attributes(doc, attributes):
    if "label" in attributes and "ent_type" not in attributes:
        if isinstance(attributes["label"], int):
            attributes[ENT_TYPE] = attributes["label"]
        else:
            attributes[ENT_TYPE] = doc.vocab.strings[attributes["label"]]
    if "ent_type" in attributes:
        attributes[ENT_TYPE] = attributes["ent_type"]


def get_entity_info(ent_info):
    if isinstance(ent_info, Span):
        ent_type = ent_info.label
        start = ent_info.start
        end = ent_info.end
    elif len(ent_info) == 3:
        ent_type, start, end = ent_info
    else:
        ent_id, ent_type, start, end = ent_info
    return ent_type, start, end
