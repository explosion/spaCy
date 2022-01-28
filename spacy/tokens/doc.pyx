# cython: infer_types=True, bounds_check=False, profile=True
cimport cython
cimport numpy as np
from libc.string cimport memcpy
from libc.math cimport sqrt
from libc.stdint cimport int32_t, uint64_t

import copy
from collections import Counter, defaultdict
from enum import Enum
import itertools
import numpy
import srsly
from thinc.api import get_array_module
from thinc.util import copy_array
import warnings

from .span cimport Span
from .token cimport MISSING_DEP
from ._dict_proxies import SpanGroups
from .token cimport Token
from ..lexeme cimport Lexeme, EMPTY_LEXEME
from ..typedefs cimport attr_t, flags_t
from ..attrs cimport attr_id_t
from ..attrs cimport LENGTH, POS, LEMMA, TAG, MORPH, DEP, HEAD, SPACY, ENT_IOB
from ..attrs cimport ENT_TYPE, ENT_ID, ENT_KB_ID, SENT_START, IDX, NORM

from ..attrs import intify_attr, IDS
from ..compat import copy_reg, pickle
from ..errors import Errors, Warnings
from ..morphology import Morphology
from .. import util
from .. import parts_of_speech
from .underscore import Underscore, get_ext_args
from ._retokenize import Retokenizer
from ._serialize import ALL_ATTRS as DOCBIN_ALL_ATTRS


DEF PADDING = 5


cdef int bounds_check(int i, int length, int padding) except -1:
    if (i + padding) < 0:
        raise IndexError(Errors.E026.format(i=i, length=length))
    if (i - padding) >= length:
        raise IndexError(Errors.E026.format(i=i, length=length))


cdef attr_t get_token_attr(const TokenC* token, attr_id_t feat_name) nogil:
    if feat_name == LEMMA:
        return token.lemma
    elif feat_name == NORM:
        if not token.norm:
            return token.lex.norm
        return token.norm
    elif feat_name == POS:
        return token.pos
    elif feat_name == TAG:
        return token.tag
    elif feat_name == MORPH:
        return token.morph
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
    elif feat_name == ENT_ID:
        return token.ent_id
    elif feat_name == ENT_KB_ID:
        return token.ent_kb_id
    elif feat_name == IDX:
        return token.idx
    else:
        return Lexeme.get_struct_attr(token.lex, feat_name)


cdef attr_t get_token_attr_for_matcher(const TokenC* token, attr_id_t feat_name) nogil:
    if feat_name == SENT_START:
        if token.sent_start == 1:
            return True
        else:
            return False
    else:
        return get_token_attr(token, feat_name)


class SetEntsDefault(str, Enum):
    blocked = "blocked"
    missing = "missing"
    outside = "outside"
    unmodified = "unmodified"

    @classmethod
    def values(cls):
        return list(cls.__members__.keys())


cdef class Doc:
    """A sequence of Token objects. Access sentences and named entities, export
    annotations to numpy arrays, losslessly serialize to compressed binary
    strings. The `Doc` object holds an array of `TokenC` structs. The
    Python-level `Token` and `Span` objects are views of this array, i.e.
    they don't own the data themselves.

    EXAMPLE:
        Construction 1
        >>> doc = nlp(u'Some text')

        Construction 2
        >>> from spacy.tokens import Doc
        >>> doc = Doc(nlp.vocab, words=["hello", "world", "!"], spaces=[True, False, False])

    DOCS: https://spacy.io/api/doc
    """

    @classmethod
    def set_extension(cls, name, **kwargs):
        """Define a custom attribute which becomes available as `Doc._`.

        name (str): Name of the attribute to set.
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

        name (str): Name of the extension.
        RETURNS (tuple): A `(default, method, getter, setter)` tuple.

        DOCS: https://spacy.io/api/doc#get_extension
        """
        return Underscore.doc_extensions.get(name)

    @classmethod
    def has_extension(cls, name):
        """Check whether an extension has been registered.

        name (str): Name of the extension.
        RETURNS (bool): Whether the extension has been registered.

        DOCS: https://spacy.io/api/doc#has_extension
        """
        return name in Underscore.doc_extensions

    @classmethod
    def remove_extension(cls, name):
        """Remove a previously registered extension.

        name (str): Name of the extension.
        RETURNS (tuple): A `(default, method, getter, setter)` tuple of the
            removed extension.

        DOCS: https://spacy.io/api/doc#remove_extension
        """
        if not cls.has_extension(name):
            raise ValueError(Errors.E046.format(name=name))
        return Underscore.doc_extensions.pop(name)

    def __init__(
        self,
        Vocab vocab,
        words=None,
        spaces=None,
        *,
        user_data=None,
        tags=None,
        pos=None,
        morphs=None,
        lemmas=None,
        heads=None,
        deps=None,
        sent_starts=None,
        ents=None,
    ):
        """Create a Doc object.

        vocab (Vocab): A vocabulary object, which must match any models you
            want to use (e.g. tokenizer, parser, entity recognizer).
        words (Optional[List[Union[str, int]]]): A list of unicode strings or
            hash values to add to the document as words. If `None`, defaults to
            empty list.
        spaces (Optional[List[bool]]): A list of boolean values, of the same
            length as `words`. `True` means that the word is followed by a space,
            `False` means it is not. If `None`, defaults to `[True]*len(words)`
        user_data (dict or None): Optional extra data to attach to the Doc.
        tags (Optional[List[str]]): A list of unicode strings, of the same
            length as words, to assign as token.tag. Defaults to None.
        pos (Optional[List[str]]): A list of unicode strings, of the same
            length as words, to assign as token.pos. Defaults to None.
        morphs (Optional[List[str]]): A list of unicode strings, of the same
            length as words, to assign as token.morph. Defaults to None.
        lemmas (Optional[List[str]]): A list of unicode strings, of the same
            length as words, to assign as token.lemma. Defaults to None.
        heads (Optional[List[int]]): A list of values, of the same length as
            words, to assign as heads. Head indices are the position of the
            head in the doc. Defaults to None.
        deps (Optional[List[str]]): A list of unicode strings, of the same
            length as words, to assign as token.dep. Defaults to None.
        sent_starts (Optional[List[Union[bool, None]]]): A list of values, of
            the same length as words, to assign as token.is_sent_start. Will be
            overridden by heads if heads is provided. Defaults to None.
        ents (Optional[List[str]]): A list of unicode strings, of the same
            length as words, as IOB tags to assign as token.ent_iob and
            token.ent_type. Defaults to None.

        DOCS: https://spacy.io/api/doc#init
        """
        self.vocab = vocab
        size = max(20, (len(words) if words is not None else 0))
        self.mem = Pool()
        self.spans = SpanGroups(self)
        # Guarantee self.lex[i-x], for any i >= 0 and x < padding is in bounds
        # However, we need to remember the true starting places, so that we can
        # realloc.
        assert size + (PADDING*2) > 0
        data_start = <TokenC*>self.mem.alloc(size + (PADDING*2), sizeof(TokenC))
        cdef int i
        for i in range(size + (PADDING*2)):
            data_start[i].lex = &EMPTY_LEXEME
            data_start[i].l_edge = i
            data_start[i].r_edge = i
        self.c = data_start + PADDING
        self.max_length = size
        self.length = 0
        self.sentiment = 0.0
        self.cats = {}
        self.user_hooks = {}
        self.user_token_hooks = {}
        self.user_span_hooks = {}
        self.tensor = numpy.zeros((0,), dtype="float32")
        self.user_data = {} if user_data is None else user_data
        self._vector = None
        self.noun_chunks_iterator = self.vocab.get_noun_chunks
        cdef bint has_space
        if words is None and spaces is not None:
            raise ValueError(Errors.E908)
        elif spaces is None and words is not None:
            self.has_unknown_spaces = True
        else:
            self.has_unknown_spaces = False
        words = words if words is not None else []
        spaces = spaces if spaces is not None else ([True] * len(words))
        if len(spaces) != len(words):
            raise ValueError(Errors.E027)
        cdef const LexemeC* lexeme
        for word, has_space in zip(words, spaces):
            if isinstance(word, str):
                lexeme = self.vocab.get(self.mem, word)
            elif isinstance(word, bytes):
                raise ValueError(Errors.E028.format(value=word))
            else:
                try:
                    lexeme = self.vocab.get_by_orth(self.mem, word)
                except TypeError:
                    raise TypeError(Errors.E1022.format(wtype=type(word)))
            self.push_back(lexeme, has_space)

        if heads is not None:
            heads = [head - i if head is not None else 0 for i, head in enumerate(heads)]
        if deps is not None:
            MISSING_DEP_ = self.vocab.strings[MISSING_DEP]
            deps = [dep if dep is not None else MISSING_DEP_ for dep in deps]
        if deps and not heads:
            heads = [0] * len(deps)
        if heads and not deps:
            raise ValueError(Errors.E1017)
        if sent_starts is not None:
            for i in range(len(sent_starts)):
                if sent_starts[i] is True:
                    sent_starts[i] = 1
                elif sent_starts[i] is False:
                    sent_starts[i] = -1
                elif sent_starts[i] is None or sent_starts[i] not in [-1, 0, 1]:
                    sent_starts[i] = 0
        if pos is not None:
            for pp in set(pos):
                if pp not in parts_of_speech.IDS:
                    raise ValueError(Errors.E1021.format(pp=pp))
        ent_iobs = None
        ent_types = None
        if ents is not None:
            iob_strings = Token.iob_strings()
            # make valid IOB2 out of IOB1 or IOB2
            for i, ent in enumerate(ents):
                if ent is "":
                    ents[i] = None
                elif ent is not None and not isinstance(ent, str):
                    raise ValueError(Errors.E177.format(tag=ent))
                if i < len(ents) - 1:
                    # OI -> OB
                    if (ent is None or ent.startswith("O")) and \
                            (ents[i+1] is not None and ents[i+1].startswith("I")):
                        ents[i+1] = "B" + ents[i+1][1:]
                    # B-TYPE1 I-TYPE2 or I-TYPE1 I-TYPE2 -> B/I-TYPE1 B-TYPE2
                    if ent is not None and ents[i+1] is not None and \
                            (ent.startswith("B") or ent.startswith("I")) and \
                            ents[i+1].startswith("I") and \
                            ent[1:] != ents[i+1][1:]:
                        ents[i+1] = "B" + ents[i+1][1:]
            ent_iobs = []
            ent_types = []
            for ent in ents:
                if ent is None:
                    ent_iobs.append(iob_strings.index(""))
                    ent_types.append("")
                elif ent == "O":
                    ent_iobs.append(iob_strings.index(ent))
                    ent_types.append("")
                else:
                    if len(ent) < 3 or ent[1] != "-":
                        raise ValueError(Errors.E177.format(tag=ent))
                    ent_iob, ent_type = ent.split("-", 1)
                    if ent_iob not in iob_strings:
                        raise ValueError(Errors.E177.format(tag=ent))
                    ent_iob = iob_strings.index(ent_iob)
                    ent_iobs.append(ent_iob)
                    ent_types.append(ent_type)
        headings = []
        values = []
        annotations = [pos, heads, deps, lemmas, tags, morphs, sent_starts, ent_iobs, ent_types]
        possible_headings = [POS, HEAD, DEP, LEMMA, TAG, MORPH, SENT_START, ENT_IOB, ENT_TYPE]
        for a, annot in enumerate(annotations):
            if annot is not None:
                if len(annot) != len(words):
                    raise ValueError(Errors.E189)
                headings.append(possible_headings[a])
                if annot is not heads and annot is not sent_starts and annot is not ent_iobs:
                    values.extend(annot)
        for value in values:
            if value is not None:
                self.vocab.strings.add(value)

        # if there are any other annotations, set them
        if headings:
            attrs = self.to_array(headings)

            j = 0
            for annot in annotations:
                if annot:
                    if annot is heads or annot is sent_starts or annot is ent_iobs:
                        for i in range(len(words)):
                            if attrs.ndim == 1:
                                attrs[i] = annot[i]
                            else:
                                attrs[i, j] = annot[i]
                    elif annot is morphs:
                        for i in range(len(words)):
                            morph_key = vocab.morphology.add(morphs[i])
                            if attrs.ndim == 1:
                                attrs[i] = morph_key
                            else:
                                attrs[i, j] = morph_key
                    else:
                        for i in range(len(words)):
                            if attrs.ndim == 1:
                                attrs[i] = self.vocab.strings[annot[i]]
                            else:
                                attrs[i, j] = self.vocab.strings[annot[i]]
                    j += 1
            self.from_array(headings, attrs)

    @property
    def _(self):
        """Custom extension attributes registered via `set_extension`."""
        return Underscore(Underscore.doc_extensions, self)

    @property
    def is_tagged(self):
        warnings.warn(Warnings.W107.format(prop="is_tagged", attr="TAG"), DeprecationWarning)
        return self.has_annotation("TAG")

    @property
    def is_parsed(self):
        warnings.warn(Warnings.W107.format(prop="is_parsed", attr="DEP"), DeprecationWarning)
        return self.has_annotation("DEP")

    @property
    def is_nered(self):
        warnings.warn(Warnings.W107.format(prop="is_nered", attr="ENT_IOB"), DeprecationWarning)
        return self.has_annotation("ENT_IOB")

    @property
    def is_sentenced(self):
        warnings.warn(Warnings.W107.format(prop="is_sentenced", attr="SENT_START"), DeprecationWarning)
        return self.has_annotation("SENT_START")

    def has_annotation(self, attr, *, require_complete=False):
        """Check whether the doc contains annotation on a token attribute.

        attr (Union[int, str]): The attribute string name or int ID.
        require_complete (bool): Whether to check that the attribute is set on
            every token in the doc.
        RETURNS (bool): Whether annotation is present.

        DOCS: https://spacy.io/api/doc#has_annotation
        """

        # empty docs are always annotated
        if self.length == 0:
            return True
        cdef int i
        cdef int range_start = 0
        if attr == "IS_SENT_START" or attr == self.vocab.strings["IS_SENT_START"]:
            attr = SENT_START
        elif attr == "IS_SENT_END" or attr == self.vocab.strings["IS_SENT_END"]:
            attr = SENT_START
        attr = intify_attr(attr)
        # adjust attributes
        if attr == HEAD:
            # HEAD does not have an unset state, so rely on DEP
            attr = DEP
        # special cases for sentence boundaries
        if attr == SENT_START:
            if "sents" in self.user_hooks:
                return True
            # docs of length 1 always have sentence boundaries
            if self.length == 1:
                return True
            range_start = 1
        if require_complete:
            return all(Token.get_struct_attr(&self.c[i], attr) for i in range(range_start, self.length))
        else:
            return any(Token.get_struct_attr(&self.c[i], attr) for i in range(range_start, self.length))

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
            start, stop = util.normalize_slice(len(self), i.start, i.stop, i.step)
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
        return self.__unicode__()

    def __repr__(self):
        return self.__str__()

    @property
    def doc(self):
        return self

    def char_span(self, int start_idx, int end_idx, label=0, kb_id=0, vector=None, alignment_mode="strict"):
        """Create a `Span` object from the slice
        `doc.text[start_idx : end_idx]`. Returns None if no valid `Span` can be
        created.

        doc (Doc): The parent document.
        start_idx (int): The index of the first character of the span.
        end_idx (int): The index of the first character after the span.
        label (uint64 or string): A label to attach to the Span, e.g. for
            named entities.
        kb_id (uint64 or string):  An ID from a KB to capture the meaning of a
            named entity.
        vector (ndarray[ndim=1, dtype='float32']): A meaning representation of
            the span.
        alignment_mode (str): How character indices are aligned to token
            boundaries. Options: "strict" (character indices must be aligned
            with token boundaries), "contract" (span of all tokens completely
            within the character span), "expand" (span of all tokens at least
            partially covered by the character span). Defaults to "strict".
        RETURNS (Span): The newly constructed object.

        DOCS: https://spacy.io/api/doc#char_span
        """
        if not isinstance(label, int):
            label = self.vocab.strings.add(label)
        if not isinstance(kb_id, int):
            kb_id = self.vocab.strings.add(kb_id)
        alignment_modes = ("strict", "contract", "expand")
        if alignment_mode not in alignment_modes:
            raise ValueError(
                Errors.E202.format(
                    name="alignment",
                    mode=alignment_mode,
                    modes=", ".join(alignment_modes),
                )
            )
        cdef int start = token_by_char(self.c, self.length, start_idx)
        if start < 0 or (alignment_mode == "strict" and start_idx != self[start].idx):
            return None
        # end_idx is exclusive, so find the token at one char before
        cdef int end = token_by_char(self.c, self.length, end_idx - 1)
        if end < 0 or (alignment_mode == "strict" and end_idx != self[end].idx + len(self[end])):
            return None
        # Adjust start and end by alignment_mode
        if alignment_mode == "contract":
            if self[start].idx < start_idx:
                start += 1
            if end_idx < self[end].idx + len(self[end]):
                end -= 1
            # if no tokens are completely within the span, return None
            if end < start:
                return None
        elif alignment_mode == "expand":
            # Don't consider the trailing whitespace to be part of the previous
            # token
            if start_idx == self[start].idx + len(self[start]):
                start += 1
        # Currently we have the token index, we want the range-end index
        end += 1
        cdef Span span = Span(self, start, end, label=label, kb_id=kb_id, vector=vector)
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
        elif isinstance(other, (Span, Doc)) and len(self) == len(other):
            similar = True
            for i in range(self.length):
                if self[i].orth != other[i].orth:
                    similar = False
                    break
            if similar:
                return 1.0
        if self.vocab.vectors.n_keys == 0:
            warnings.warn(Warnings.W007.format(obj="Doc"))
        if self.vector_norm == 0 or other.vector_norm == 0:
            warnings.warn(Warnings.W008.format(obj="Doc"))
            return 0.0
        vector = self.vector
        xp = get_array_module(vector)
        result = xp.dot(vector, other.vector) / (self.vector_norm * other.vector_norm)
        # ensure we get a scalar back (numpy does this automatically but cupy doesn't)
        return result.item()

    @property
    def has_vector(self):
        """A boolean value indicating whether a word vector is associated with
        the object.

        RETURNS (bool): Whether a word vector is associated with the object.

        DOCS: https://spacy.io/api/doc#has_vector
        """
        if "has_vector" in self.user_hooks:
            return self.user_hooks["has_vector"](self)
        elif self.vocab.vectors.size:
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
            xp = get_array_module(self.vocab.vectors.data)
            if not len(self):
                self._vector = xp.zeros((self.vocab.vectors_length,), dtype="f")
                return self._vector
            elif self.vocab.vectors.size > 0:
                self._vector = sum(t.vector for t in self) / len(self)
                return self._vector
            elif self.tensor.size > 0:
                self._vector = self.tensor.mean(axis=0)
                return self._vector
            else:
                return xp.zeros((self.vocab.vectors_length,), dtype="float32")

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

        RETURNS (str): The original verbatim text of the document.
        """
        return "".join(t.text_with_ws for t in self)

    @property
    def text_with_ws(self):
        """An alias of `Doc.text`, provided for duck-type compatibility with
        `Span` and `Token`.

        RETURNS (str): The original verbatim text of the document.
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
            cdef attr_t kb_id = 0
            output = []
            for i in range(self.length):
                token = &self.c[i]
                if token.ent_iob == 1:
                    if start == -1:
                        seq = [f"{t.text}|{t.ent_iob_}" for t in self[i-5:i+5]]
                        raise ValueError(Errors.E093.format(seq=" ".join(seq)))
                elif token.ent_iob == 2 or token.ent_iob == 0 or \
                        (token.ent_iob == 3 and token.ent_type == 0):
                    if start != -1:
                        output.append(Span(self, start, i, label=label, kb_id=kb_id))
                    start = -1
                    label = 0
                    kb_id = 0
                elif token.ent_iob == 3:
                    if start != -1:
                        output.append(Span(self, start, i, label=label, kb_id=kb_id))
                    start = i
                    label = token.ent_type
                    kb_id = token.ent_kb_id
            if start != -1:
                output.append(Span(self, start, self.length, label=label, kb_id=kb_id))
            # remove empty-label spans
            output = [o for o in output if o.label_ != ""]
            return tuple(output)

        def __set__(self, ents):
            # TODO:
            # 1. Test basic data-driven ORTH gazetteer
            # 2. Test more nuanced date and currency regex
            cdef attr_t entity_type, kb_id
            cdef int ent_start, ent_end
            ent_spans = []
            for ent_info in ents:
                entity_type_, kb_id, ent_start, ent_end = get_entity_info(ent_info)
                if isinstance(entity_type_, str):
                    self.vocab.strings.add(entity_type_)
                span = Span(self, ent_start, ent_end, label=entity_type_, kb_id=kb_id)
                ent_spans.append(span)
            self.set_ents(ent_spans, default=SetEntsDefault.outside)

    def set_ents(self, entities, *, blocked=None, missing=None, outside=None, default=SetEntsDefault.outside):
        """Set entity annotation.

        entities (List[Span]): Spans with labels to set as entities.
        blocked (Optional[List[Span]]): Spans to set as 'blocked' (never an
            entity) for spacy's built-in NER component. Other components may
            ignore this setting.
        missing (Optional[List[Span]]): Spans with missing/unknown entity
            information.
        outside (Optional[List[Span]]): Spans outside of entities (O in IOB).
        default (str): How to set entity annotation for tokens outside of any
            provided spans. Options: "blocked", "missing", "outside" and
            "unmodified" (preserve current state). Defaults to "outside".
        """
        if default not in SetEntsDefault.values():
            raise ValueError(Errors.E1011.format(default=default, modes=", ".join(SetEntsDefault)))

        # Ignore spans with missing labels
        entities = [ent for ent in entities if ent.label > 0]

        if blocked is None:
            blocked = tuple()
        if missing is None:
            missing = tuple()
        if outside is None:
            outside = tuple()

        # Find all tokens covered by spans and check that none are overlapping
        cdef int i
        seen_tokens = set()
        for span in itertools.chain.from_iterable([entities, blocked, missing, outside]):
            if not isinstance(span, Span):
                raise ValueError(Errors.E1012.format(span=span))
            for i in range(span.start, span.end):
                if i in seen_tokens:
                    raise ValueError(Errors.E1010.format(i=i))
                seen_tokens.add(i)

        # Set all specified entity information
        for span in entities:
            for i in range(span.start, span.end):
                if i == span.start:
                    self.c[i].ent_iob = 3
                else:
                    self.c[i].ent_iob = 1
                self.c[i].ent_type = span.label
                self.c[i].ent_kb_id = span.kb_id
        for span in blocked:
            for i in range(span.start, span.end):
                self.c[i].ent_iob = 3
                self.c[i].ent_type = 0
        for span in missing:
            for i in range(span.start, span.end):
                self.c[i].ent_iob = 0
                self.c[i].ent_type = 0
        for span in outside:
            for i in range(span.start, span.end):
                self.c[i].ent_iob = 2
                self.c[i].ent_type = 0

        # Set tokens outside of all provided spans
        if default != SetEntsDefault.unmodified:
            for i in range(self.length):
                if i not in seen_tokens:
                    self.c[i].ent_type = 0
                    if default == SetEntsDefault.outside:
                        self.c[i].ent_iob = 2
                    elif default == SetEntsDefault.missing:
                        self.c[i].ent_iob = 0
                    elif default == SetEntsDefault.blocked:
                        self.c[i].ent_iob = 3

        # Fix any resulting inconsistent annotation
        for i in range(self.length - 1):
            # I must follow B or I: convert I to B
            if (self.c[i].ent_iob == 0 or self.c[i].ent_iob == 2) and \
                    self.c[i+1].ent_iob == 1:
                self.c[i+1].ent_iob = 3
            # Change of type with BI or II: convert second I to B
            if self.c[i].ent_type != self.c[i+1].ent_type and \
                    (self.c[i].ent_iob == 3 or self.c[i].ent_iob == 1) and \
                    self.c[i+1].ent_iob == 1:
                self.c[i+1].ent_iob = 3

    @property
    def noun_chunks(self):
        """Iterate over the base noun phrases in the document. Yields base
        noun-phrase #[code Span] objects, if the language has a noun chunk iterator.
        Raises a NotImplementedError otherwise.

        A base noun phrase, or "NP chunk", is a noun
        phrase that does not permit other NPs to be nested within it – so no
        NP-level coordination, no prepositional phrases, and no relative
        clauses.

        YIELDS (Span): Noun chunks in the document.

        DOCS: https://spacy.io/api/doc#noun_chunks
        """
        if self.noun_chunks_iterator is None:
            raise NotImplementedError(Errors.E894.format(lang=self.vocab.lang))

        # Accumulate the result before beginning to iterate over it. This
        # prevents the tokenization from being changed out from under us
        # during the iteration. The tricky thing here is that Span accepts
        # its tokenization changing, so it's okay once we have the Span
        # objects. See Issue #375.
        spans = []
        for start, end, label in self.noun_chunks_iterator(self):
            spans.append(Span(self, start, end, label=label))
        for span in spans:
            yield span

    @property
    def sents(self):
        """Iterate over the sentences in the document. Yields sentence `Span`
        objects. Sentence spans have no label.

        YIELDS (Span): Sentences in the document.

        DOCS: https://spacy.io/api/doc#sents
        """
        if not self.has_annotation("SENT_START"):
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
        """RETURNS (str): Language of the doc's vocabulary, e.g. 'en'."""
        return self.vocab.lang

    cdef int push_back(self, LexemeOrToken lex_or_tok, bint has_space) except -1:
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

        py_attr_ids (list[]): A list of attributes (int IDs or string names).
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
        if isinstance(py_attr_ids, str):
            # Handle inputs like doc.to_array('ORTH')
            py_attr_ids = [py_attr_ids]
        elif not hasattr(py_attr_ids, "__iter__"):
            # Handle inputs like doc.to_array(ORTH)
            py_attr_ids = [py_attr_ids]
        # Allow strings, e.g. 'lemma' or 'LEMMA'
        try:
            py_attr_ids = [(IDS[id_.upper()] if hasattr(id_, "upper") else id_)
                       for id_ in py_attr_ids]
        except KeyError as msg:
            keys = [k for k in IDS.keys() if not k.startswith("FLAG")]
            raise KeyError(Errors.E983.format(dict="IDS", key=msg, keys=keys)) from None
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

    def count_by(self, attr_id_t attr_id, exclude=None, object counts=None):
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
            counts = Counter()
            output_dict = True
        else:
            output_dict = False
        # Take this check out of the loop, for a bit of extra speed
        if exclude is None:
            for i in range(self.length):
                counts[get_token_attr(&self.c[i], attr_id)] += 1
        else:
            for i in range(self.length):
                if not exclude(self[i]):
                    counts[get_token_attr(&self.c[i], attr_id)] += 1
        if output_dict:
            return dict(counts)

    def _realloc(self, new_size):
        if new_size < self.max_length:
            return
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
        if isinstance(attrs, str):
            # Handle inputs like doc.to_array('ORTH')
            attrs = [attrs]
        elif not hasattr(attrs, "__iter__"):
            # Handle inputs like doc.to_array(ORTH)
            attrs = [attrs]
        # Allow strings, e.g. 'lemma' or 'LEMMA'
        attrs = [(IDS[id_.upper()] if hasattr(id_, "upper") else id_)
                 for id_ in attrs]
        if array.dtype != numpy.uint64:
            warnings.warn(Warnings.W028.format(type=array.dtype))

        cdef int i, col
        cdef int32_t abs_head_index
        cdef attr_id_t attr_id
        cdef TokenC* tokens = self.c
        cdef int length = len(array)
        if length != len(self):
            raise ValueError(Errors.E971.format(array_length=length, doc_length=len(self)))

        # Get set up for fast loading
        cdef Pool mem = Pool()
        cdef int n_attrs = len(attrs)
        # attrs should not be empty, but make sure to avoid zero-length mem alloc
        assert n_attrs > 0
        attr_ids = <attr_id_t*>mem.alloc(n_attrs, sizeof(attr_id_t))
        for i, attr_id in enumerate(attrs):
            attr_ids[i] = attr_id
        if len(array.shape) == 1:
            array = array.reshape((array.size, 1))
        cdef np.ndarray transposed_array = numpy.ascontiguousarray(array.T)
        values = <const uint64_t*>transposed_array.data
        stride = transposed_array.shape[1]
        # Check that all heads are within the document bounds
        if HEAD in attrs:
            col = attrs.index(HEAD)
            for i in range(length):
                # cast index to signed int
                abs_head_index = <int32_t>values[col * stride + i]
                abs_head_index += i
                if abs_head_index < 0 or abs_head_index >= length:
                    raise ValueError(
                        Errors.E190.format(
                            index=i,
                            value=array[i, col],
                            rel_head_index=abs_head_index-i
                        )
                    )
        # Verify ENT_IOB are proper integers
        if ENT_IOB in attrs:
            iob_strings = Token.iob_strings()
            col = attrs.index(ENT_IOB)
            n_iob_strings = len(iob_strings)
            for i in range(length):
                value = values[col * stride + i]
                if value < 0 or value >= n_iob_strings:
                    raise ValueError(
                        Errors.E982.format(
                            values=iob_strings,
                            value=value
                        )
                    )
        # Now load the data
        for i in range(length):
            token = &self.c[i]
            for j in range(n_attrs):
                value = values[j * stride + i]
                if attr_ids[j] == MORPH:
                    # add morph to morphology table
                    self.vocab.morphology.add(self.vocab.strings[value])
                Token.set_struct_attr(token, attr_ids[j], value)
        # If document is parsed, set children and sentence boundaries
        if HEAD in attrs and DEP in attrs:
            col = attrs.index(DEP)
            if array[:, col].any():
                set_children_from_heads(self.c, 0, length)
        return self

    @staticmethod
    def from_docs(docs, ensure_whitespace=True, attrs=None):
        """Concatenate multiple Doc objects to form a new one. Raises an error
        if the `Doc` objects do not all share the same `Vocab`.

        docs (list): A list of Doc objects.
        ensure_whitespace (bool): Insert a space between two adjacent docs whenever the first doc does not end in whitespace.
        attrs (list): Optional list of attribute ID ints or attribute name strings.
        RETURNS (Doc): A doc that contains the concatenated docs, or None if no docs were given.

        DOCS: https://spacy.io/api/doc#from_docs
        """
        if not docs:
            return None

        vocab = {doc.vocab for doc in docs}
        if len(vocab) > 1:
            raise ValueError(Errors.E999)
        (vocab,) = vocab

        if attrs is None:
            attrs = list(Doc._get_array_attrs())
        else:
            if any(isinstance(attr, str) for attr in attrs):     # resolve attribute names
                attrs = [intify_attr(attr) for attr in attrs]    # intify_attr returns None for invalid attrs
            attrs = list(attr for attr in set(attrs) if attr)    # filter duplicates, remove None if present
        if SPACY not in attrs:
            attrs.append(SPACY)

        concat_words = []
        concat_spaces = []
        concat_user_data = {}
        concat_spans = defaultdict(list)
        char_offset = 0
        for doc in docs:
            concat_words.extend(t.text for t in doc)
            concat_spaces.extend(bool(t.whitespace_) for t in doc)

            for key, value in doc.user_data.items():
                if isinstance(key, tuple) and len(key) == 4 and key[0] == "._.":
                    data_type, name, start, end = key
                    if start is not None or end is not None:
                        start += char_offset
                        if end is not None:
                            end += char_offset
                        concat_user_data[(data_type, name, start, end)] = copy.copy(value)
                    else:
                        warnings.warn(Warnings.W101.format(name=name))
                else:
                    warnings.warn(Warnings.W102.format(key=key, value=value))
            for key in doc.spans:
                # if a spans key is in any doc, include it in the merged doc
                # even if it is empty
                if key not in concat_spans:
                    concat_spans[key] = []
                for span in doc.spans[key]:
                    concat_spans[key].append((
                        span.start_char + char_offset,
                        span.end_char + char_offset,
                        span.label,
                        span.kb_id,
                        span.text, # included as a check
                    ))
            char_offset += len(doc.text)
            if len(doc) > 0 and ensure_whitespace and not doc[-1].is_space and not bool(doc[-1].whitespace_):
                char_offset += 1

        arrays = [doc.to_array(attrs) for doc in docs]

        if ensure_whitespace:
            spacy_index = attrs.index(SPACY)
            for i, array in enumerate(arrays[:-1]):
                if len(array) > 0 and not docs[i][-1].is_space:
                    array[-1][spacy_index] = 1
            if len(concat_spaces) > 0:
                token_offset = -1
                for doc in docs[:-1]:
                    token_offset += len(doc)
                    if len(doc) > 0 and not doc[-1].is_space:
                        concat_spaces[token_offset] = True

        concat_array = numpy.concatenate(arrays)

        concat_doc = Doc(vocab, words=concat_words, spaces=concat_spaces, user_data=concat_user_data)

        concat_doc.from_array(attrs, concat_array)

        for key in concat_spans:
            if key not in concat_doc.spans:
                concat_doc.spans[key] = []
            for span_tuple in concat_spans[key]:
                span = concat_doc.char_span(
                        span_tuple[0],
                        span_tuple[1],
                        label=span_tuple[2],
                        kb_id=span_tuple[3],
                )
                text = span_tuple[4]
                if span is not None and span.text == text:
                    concat_doc.spans[key].append(span)
                else:
                    raise ValueError(Errors.E873.format(key=key, text=text))

        return concat_doc

    def get_lca_matrix(self):
        """Calculates a matrix of Lowest Common Ancestors (LCA) for a given
        `Doc`, where LCA[i, j] is the index of the lowest common ancestor among
        token i and j.

        RETURNS (np.array[ndim=2, dtype=numpy.int32]): LCA matrix with shape
            (n, n), where n = len(self).

        DOCS: https://spacy.io/api/doc#get_lca_matrix
        """
        return numpy.asarray(_get_lca_matrix(self, 0, len(self)))

    def copy(self):
        cdef Doc other = Doc(self.vocab)
        other._vector = copy.deepcopy(self._vector)
        other._vector_norm = copy.deepcopy(self._vector_norm)
        other.tensor = copy.deepcopy(self.tensor)
        other.cats = copy.deepcopy(self.cats)
        other.user_data = copy.deepcopy(self.user_data)
        other.sentiment = self.sentiment
        other.has_unknown_spaces = self.has_unknown_spaces
        other.user_hooks = dict(self.user_hooks)
        other.user_token_hooks = dict(self.user_token_hooks)
        other.user_span_hooks = dict(self.user_span_hooks)
        other.length = self.length
        other.max_length = self.max_length
        other.spans = self.spans.copy(doc=other)
        buff_size = other.max_length + (PADDING*2)
        assert buff_size > 0
        tokens = <TokenC*>other.mem.alloc(buff_size, sizeof(TokenC))
        memcpy(tokens, self.c - PADDING, buff_size * sizeof(TokenC))
        other.c = &tokens[PADDING]
        return other

    def to_disk(self, path, *, exclude=tuple()):
        """Save the current state to a directory.

        path (str / Path): A path to a directory, which will be created if
            it doesn't exist. Paths may be either strings or Path-like objects.
        exclude (Iterable[str]): String names of serialization fields to exclude.

        DOCS: https://spacy.io/api/doc#to_disk
        """
        path = util.ensure_path(path)
        with path.open("wb") as file_:
            file_.write(self.to_bytes(exclude=exclude))

    def from_disk(self, path, *, exclude=tuple()):
        """Loads state from a directory. Modifies the object in place and
        returns it.

        path (str / Path): A path to a directory. Paths may be either
            strings or `Path`-like objects.
        exclude (list): String names of serialization fields to exclude.
        RETURNS (Doc): The modified `Doc` object.

        DOCS: https://spacy.io/api/doc#from_disk
        """
        path = util.ensure_path(path)
        with path.open("rb") as file_:
            bytes_data = file_.read()
        return self.from_bytes(bytes_data, exclude=exclude)

    def to_bytes(self, *, exclude=tuple()):
        """Serialize, i.e. export the document contents to a binary string.

        exclude (list): String names of serialization fields to exclude.
        RETURNS (bytes): A losslessly serialized copy of the `Doc`, including
            all annotations.

        DOCS: https://spacy.io/api/doc#to_bytes
        """
        return srsly.msgpack_dumps(self.to_dict(exclude=exclude))

    def from_bytes(self, bytes_data, *, exclude=tuple()):
        """Deserialize, i.e. import the document contents from a binary string.

        data (bytes): The string to load from.
        exclude (list): String names of serialization fields to exclude.
        RETURNS (Doc): Itself.

        DOCS: https://spacy.io/api/doc#from_bytes
        """
        return self.from_dict(srsly.msgpack_loads(bytes_data), exclude=exclude)

    def to_dict(self, *, exclude=tuple()):
        """Export the document contents to a dictionary for serialization.

        exclude (list): String names of serialization fields to exclude.
        RETURNS (bytes): A losslessly serialized copy of the `Doc`, including
            all annotations.

        DOCS: https://spacy.io/api/doc#to_bytes
        """
        array_head = Doc._get_array_attrs()
        strings = set()
        for token in self:
            strings.add(token.tag_)
            strings.add(token.lemma_)
            strings.add(str(token.morph))
            strings.add(token.dep_)
            strings.add(token.ent_type_)
            strings.add(token.ent_kb_id_)
            strings.add(token.ent_id_)
            strings.add(token.norm_)
        for group in self.spans.values():
            for span in group:
                strings.add(span.label_)
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
            "cats": lambda: self.cats,
            "spans": lambda: self.spans.to_bytes(),
            "strings": lambda: list(strings),
            "has_unknown_spaces": lambda: self.has_unknown_spaces
        }
        if "user_data" not in exclude and self.user_data:
            user_data_keys, user_data_values = list(zip(*self.user_data.items()))
            if "user_data_keys" not in exclude:
                serializers["user_data_keys"] = lambda: srsly.msgpack_dumps(user_data_keys)
            if "user_data_values" not in exclude:
                serializers["user_data_values"] = lambda: srsly.msgpack_dumps(user_data_values)
        if "user_hooks" not in exclude and any((self.user_hooks, self.user_token_hooks, self.user_span_hooks)):
            warnings.warn(Warnings.W109)
        return util.to_dict(serializers, exclude)

    def from_dict(self, msg, *, exclude=tuple()):
        """Deserialize, i.e. import the document contents from a binary string.

        data (bytes): The string to load from.
        exclude (list): String names of serialization fields to exclude.
        RETURNS (Doc): Itself.

        DOCS: https://spacy.io/api/doc#from_dict
        """
        if self.length != 0:
            raise ValueError(Errors.E033.format(length=self.length))
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
        if "cats" not in exclude and "cats" in msg:
            self.cats = msg["cats"]
        if "strings" not in exclude and "strings" in msg:
            for s in msg["strings"]:
                self.vocab.strings.add(s)
        if "has_unknown_spaces" not in exclude and "has_unknown_spaces" in msg:
            self.has_unknown_spaces = msg["has_unknown_spaces"]
        start = 0
        cdef const LexemeC* lex
        cdef str orth_
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
        if "spans" in msg:
            self.spans.from_bytes(msg["spans"])
        else:
            self.spans.clear()
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
            intersections empty. Cannot be empty.
        attributes (Dictionary[]): Attributes to assign to the merged tokens. By default,
            must be the same length as spans, empty dictionaries are allowed.
            attributes are inherited from the syntactic root of the span.
        RETURNS (Token): The first newly merged token.
        """
        cdef str tag, lemma, ent_type
        attr_len = len(attributes)
        span_len = len(spans)
        if not attr_len == span_len:
            raise ValueError(Errors.E121.format(attr_len=attr_len, span_len=span_len))
        with self.retokenize() as retokenizer:
            for i, span in enumerate(spans):
                fix_attributes(self, attributes[i])
                remove_label_if_necessary(attributes[i])
                retokenizer.merge(span, attributes[i])

    def to_json(self, underscore=None):
        """Convert a Doc to JSON.

        underscore (list): Optional list of string names of custom doc._.
        attributes. Attribute values need to be JSON-serializable. Values will
        be added to an "_" key in the data, e.g. "_": {"foo": "bar"}.
        RETURNS (dict): The data in spaCy's JSON format.
        """
        data = {"text": self.text}
        if self.has_annotation("ENT_IOB"):
            data["ents"] = [{"start": ent.start_char, "end": ent.end_char,
                            "label": ent.label_} for ent in self.ents]
        if self.has_annotation("SENT_START"):
            sents = list(self.sents)
            data["sents"] = [{"start": sent.start_char, "end": sent.end_char}
                             for sent in sents]
        if self.cats:
            data["cats"] = self.cats
        data["tokens"] = []
        attrs = ["TAG", "MORPH", "POS", "LEMMA", "DEP"]
        include_annotation = {attr: self.has_annotation(attr) for attr in attrs}
        for token in self:
            token_data = {"id": token.i, "start": token.idx, "end": token.idx + len(token)}
            if include_annotation["TAG"]:
                token_data["tag"] = token.tag_
            if include_annotation["POS"]:
                token_data["pos"] = token.pos_
            if include_annotation["MORPH"]:
                token_data["morph"] = token.morph.to_json()
            if include_annotation["LEMMA"]:
                token_data["lemma"] = token.lemma_
            if include_annotation["DEP"]:
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

    def to_utf8_array(self, int nr_char=-1):
        """Encode word strings to utf8, and export to a fixed-width array
        of characters. Characters are placed into the array in the order:
            0, -1, 1, -2, etc
        For example, if the array is sliced array[:, :8], the array will
        contain the first 4 characters and last 4 characters of each word ---
        with the middle characters clipped out. The value 255 is used as a pad
        value.
        """
        byte_strings = [token.orth_.encode('utf8') for token in self]
        if nr_char == -1:
            nr_char = max(len(bs) for bs in byte_strings)
        cdef np.ndarray output = numpy.zeros((len(byte_strings), nr_char), dtype='uint8')
        output.fill(255)
        cdef int i, j, start_idx, end_idx
        cdef bytes byte_string
        cdef unsigned char utf8_char
        for i, byte_string in enumerate(byte_strings):
            j = 0
            start_idx = 0
            end_idx = len(byte_string) - 1
            while j < nr_char and start_idx <= end_idx:
                output[i, j] = <unsigned char>byte_string[start_idx]
                start_idx += 1
                j += 1
                if j < nr_char and start_idx <= end_idx:
                    output[i, j] = <unsigned char>byte_string[end_idx]
                    end_idx -= 1
                    j += 1
        return output

    @staticmethod
    def _get_array_attrs():
        attrs = [LENGTH, SPACY]
        attrs.extend(intify_attr(x) for x in DOCBIN_ALL_ATTRS)
        return tuple(attrs)


cdef int token_by_start(const TokenC* tokens, int length, int start_char) except -2:
    cdef int i = token_by_char(tokens, length, start_char)
    if i >= 0 and tokens[i].idx == start_char:
        return i
    else:
        return -1


cdef int token_by_end(const TokenC* tokens, int length, int end_char) except -2:
    # end_char is exclusive, so find the token at one char before
    cdef int i = token_by_char(tokens, length, end_char - 1)
    if i >= 0 and tokens[i].idx + tokens[i].lex.length == end_char:
        return i
    else:
        return -1


cdef int token_by_char(const TokenC* tokens, int length, int char_idx) except -2:
    cdef int start = 0, mid, end = length - 1
    while start <= end:
        mid = (start + end) / 2
        if char_idx < tokens[mid].idx:
            end = mid - 1
        elif char_idx >= tokens[mid].idx + tokens[mid].lex.length + tokens[mid].spacy:
            start = mid + 1
        else:
            return mid
    return -1

cdef int set_children_from_heads(TokenC* tokens, int start, int end) except -1:
    # note: end is exclusive
    cdef TokenC* head
    cdef TokenC* child
    cdef int i
    # Set number of left/right children to 0. We'll increment it in the loops.
    for i in range(start, end):
        tokens[i].l_kids = 0
        tokens[i].r_kids = 0
        tokens[i].l_edge = i
        tokens[i].r_edge = i
    cdef int loop_count = 0
    cdef bint heads_within_sents = False
    # Try up to 10 iterations of adjusting lr_kids and lr_edges in order to
    # handle non-projective dependency parses, stopping when all heads are
    # within their respective sentence boundaries. We have documented cases
    # that need at least 4 iterations, so this is to be on the safe side
    # without risking getting stuck in an infinite loop if something is
    # terribly malformed.
    while not heads_within_sents:
        heads_within_sents = _set_lr_kids_and_edges(tokens, start, end, loop_count)
        if loop_count > 10:
            util.logger.debug(Warnings.W026)
            break
        loop_count += 1
    # Set sentence starts
    for i in range(start, end):
        tokens[i].sent_start = -1
    for i in range(start, end):
        if tokens[i].head == 0 and not Token.missing_head(&tokens[i]):
            tokens[tokens[i].l_edge].sent_start = 1


cdef int _set_lr_kids_and_edges(TokenC* tokens, int start, int end, int loop_count) except -1:
    # May be called multiple times due to non-projectivity. See issues #3170
    # and #4688.
    # Set left edges
    cdef TokenC* head
    cdef TokenC* child
    cdef int i, j
    for i in range(start, end):
        child = &tokens[i]
        head = &tokens[i + child.head]
        if loop_count == 0 and child < head:
            head.l_kids += 1
        if child.l_edge < head.l_edge:
            head.l_edge = child.l_edge
        if child.r_edge > head.r_edge:
            head.r_edge = child.r_edge
    # Set right edges - same as above, but iterate in reverse
    for i in range(end-1, start-1, -1):
        child = &tokens[i]
        head = &tokens[i + child.head]
        if loop_count == 0 and child > head:
            head.r_kids += 1
        if child.r_edge > head.r_edge:
            head.r_edge = child.r_edge
        if child.l_edge < head.l_edge:
            head.l_edge = child.l_edge
    # Get sentence start positions according to current state
    sent_starts = set()
    for i in range(start, end):
        if tokens[i].head == 0:
            sent_starts.add(tokens[i].l_edge)
    cdef int curr_sent_start = 0
    cdef int curr_sent_end = 0
    # Check whether any heads are not within the current sentence
    for i in range(start, end):
        if (i > 0 and i in sent_starts) or i == end - 1:
            curr_sent_end = i
            for j in range(curr_sent_start, curr_sent_end):
                if tokens[j].head + j < curr_sent_start or tokens[j].head + j >= curr_sent_end + 1:
                    return False
            curr_sent_start = i
    return True


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
    cdef int j, k
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
        max_range = min(j + n_missing_tokens_in_sent, end - start)
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
    bytes_data = doc.to_bytes(exclude=["vocab", "user_data", "user_hooks"])
    hooks_and_data = (doc.user_data, doc.user_hooks, doc.user_span_hooks,
                      doc.user_token_hooks, doc._context)
    return (unpickle_doc, (doc.vocab, srsly.pickle_dumps(hooks_and_data), bytes_data))


def unpickle_doc(vocab, hooks_and_data, bytes_data):
    user_data, doc_hooks, span_hooks, token_hooks, _context = srsly.pickle_loads(hooks_and_data)

    doc = Doc(vocab, user_data=user_data).from_bytes(bytes_data, exclude=["user_data"])
    doc.user_hooks.update(doc_hooks)
    doc.user_span_hooks.update(span_hooks)
    doc.user_token_hooks.update(token_hooks)
    doc._context = _context
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
        ent_kb_id = ent_info.kb_id
        start = ent_info.start
        end = ent_info.end
    elif len(ent_info) == 3:
        ent_type, start, end = ent_info
        ent_kb_id = 0
    elif len(ent_info) == 4:
        ent_type, ent_kb_id, start, end = ent_info
    else:
        ent_id, ent_kb_id, ent_type, start, end = ent_info
    return ent_type, ent_kb_id, start, end
