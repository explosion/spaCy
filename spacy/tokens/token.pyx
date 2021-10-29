# cython: infer_types=True
# Compiler crashes on memory view coercion without this. Should report bug.
from cython.view cimport array as cvarray
cimport numpy as np
np.import_array()

import numpy
from thinc.api import get_array_module
import warnings

from ..typedefs cimport hash_t
from ..lexeme cimport Lexeme
from ..attrs cimport IS_ALPHA, IS_ASCII, IS_DIGIT, IS_LOWER, IS_PUNCT, IS_SPACE
from ..attrs cimport IS_BRACKET, IS_QUOTE, IS_LEFT_PUNCT, IS_RIGHT_PUNCT
from ..attrs cimport IS_TITLE, IS_UPPER, IS_CURRENCY, IS_STOP
from ..attrs cimport LIKE_URL, LIKE_NUM, LIKE_EMAIL
from ..symbols cimport conj
from .morphanalysis cimport MorphAnalysis
from .doc cimport set_children_from_heads

from .. import parts_of_speech
from ..errors import Errors, Warnings
from .underscore import Underscore, get_ext_args


cdef class Token:
    """An individual token – i.e. a word, punctuation symbol, whitespace,
    etc.

    DOCS: https://spacy.io/api/token
    """
    @classmethod
    def set_extension(cls, name, **kwargs):
        """Define a custom attribute which becomes available as `Token._`.

        name (str): Name of the attribute to set.
        default: Optional default value of the attribute.
        getter (callable): Optional getter function.
        setter (callable): Optional setter function.
        method (callable): Optional method for method extension.
        force (bool): Force overwriting existing attribute.

        DOCS: https://spacy.io/api/token#set_extension
        USAGE: https://spacy.io/usage/processing-pipelines#custom-components-attributes
        """
        if cls.has_extension(name) and not kwargs.get("force", False):
            raise ValueError(Errors.E090.format(name=name, obj="Token"))
        Underscore.token_extensions[name] = get_ext_args(**kwargs)

    @classmethod
    def get_extension(cls, name):
        """Look up a previously registered extension by name.

        name (str): Name of the extension.
        RETURNS (tuple): A `(default, method, getter, setter)` tuple.

        DOCS: https://spacy.io/api/token#get_extension
        """
        return Underscore.token_extensions.get(name)

    @classmethod
    def has_extension(cls, name):
        """Check whether an extension has been registered.

        name (str): Name of the extension.
        RETURNS (bool): Whether the extension has been registered.

        DOCS: https://spacy.io/api/token#has_extension
        """
        return name in Underscore.token_extensions

    @classmethod
    def remove_extension(cls, name):
        """Remove a previously registered extension.

        name (str): Name of the extension.
        RETURNS (tuple): A `(default, method, getter, setter)` tuple of the
            removed extension.

        DOCS: https://spacy.io/api/token#remove_extension
        """
        if not cls.has_extension(name):
            raise ValueError(Errors.E046.format(name=name))
        return Underscore.token_extensions.pop(name)

    def __cinit__(self, Vocab vocab, Doc doc, int offset):
        """Construct a `Token` object.

        vocab (Vocab): A storage container for lexical types.
        doc (Doc): The parent document.
        offset (int): The index of the token within the document.

        DOCS: https://spacy.io/api/token#init
        """
        self.vocab = vocab
        self.doc = doc
        self.c = &self.doc.c[offset]
        self.i = offset

    def __hash__(self):
        return hash((self.doc, self.i))

    def __len__(self):
        """The number of unicode characters in the token, i.e. `token.text`.

        RETURNS (int): The number of unicode characters in the token.

        DOCS: https://spacy.io/api/token#len
        """
        return self.c.lex.length

    def __unicode__(self):
        return self.text

    def __bytes__(self):
        return self.text.encode('utf8')

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__str__()

    def __richcmp__(self, Token other, int op):
        # http://cython.readthedocs.io/en/latest/src/userguide/special_methods.html
        if other is None:
            if op in (0, 1, 2):
                return False
            else:
                return True
        cdef Doc my_doc = self.doc
        cdef Doc other_doc = other.doc
        my = self.idx
        their = other.idx
        if op == 0:
            return my < their
        elif op == 2:
            if my_doc is other_doc:
                return my == their
            else:
                return False
        elif op == 4:
            return my > their
        elif op == 1:
            return my <= their
        elif op == 3:
            if my_doc is other_doc:
                return my != their
            else:
                return True
        elif op == 5:
            return my >= their
        else:
            raise ValueError(Errors.E041.format(op=op))

    def __reduce__(self):
        raise NotImplementedError(Errors.E111)

    @property
    def _(self):
        """Custom extension attributes registered via `set_extension`."""
        return Underscore(Underscore.token_extensions, self,
                          start=self.idx, end=None)

    cpdef bint check_flag(self, attr_id_t flag_id) except -1:
        """Check the value of a boolean flag.

        flag_id (int): The ID of the flag attribute.
        RETURNS (bool): Whether the flag is set.

        DOCS: https://spacy.io/api/token#check_flag
        """
        return Lexeme.c_check_flag(self.c.lex, flag_id)

    def nbor(self, int i=1):
        """Get a neighboring token.

        i (int): The relative position of the token to get. Defaults to 1.
        RETURNS (Token): The token at position `self.doc[self.i+i]`.

        DOCS: https://spacy.io/api/token#nbor
        """
        if self.i+i < 0 or (self.i+i >= len(self.doc)):
            raise IndexError(Errors.E042.format(i=self.i, j=i, length=len(self.doc)))
        return self.doc[self.i+i]

    def similarity(self, other):
        """Make a semantic similarity estimate. The default estimate is cosine
        similarity using an average of word vectors.

        other (object): The object to compare with. By default, accepts `Doc`,
            `Span`, `Token` and `Lexeme` objects.
        RETURNS (float): A scalar similarity score. Higher is more similar.

        DOCS: https://spacy.io/api/token#similarity
        """
        if "similarity" in self.doc.user_token_hooks:
            return self.doc.user_token_hooks["similarity"](self, other)
        if hasattr(other, "__len__") and len(other) == 1 and hasattr(other, "__getitem__"):
            if self.c.lex.orth == getattr(other[0], "orth", None):
                return 1.0
        elif hasattr(other, "orth"):
            if self.c.lex.orth == other.orth:
                return 1.0
        if self.vocab.vectors.n_keys == 0:
            warnings.warn(Warnings.W007.format(obj="Token"))
        if self.vector_norm == 0 or other.vector_norm == 0:
            warnings.warn(Warnings.W008.format(obj="Token"))
            return 0.0
        vector = self.vector
        xp = get_array_module(vector)
        return (xp.dot(vector, other.vector) / (self.vector_norm * other.vector_norm))

    def has_morph(self):
        """Check whether the token has annotated morph information.
        Return False when the morph annotation is unset/missing.

        RETURNS (bool): Whether the morph annotation is set.
        """
        return not self.c.morph == 0

    property morph:
        def __get__(self):
            return MorphAnalysis.from_id(self.vocab, self.c.morph)

        def __set__(self, MorphAnalysis morph):
            # Check that the morph has the same vocab
            if self.vocab != morph.vocab:
                raise ValueError(Errors.E1013)
            self.c.morph = morph.c.key

    def set_morph(self, features):
        cdef hash_t key
        if features is None:
            self.c.morph = 0
        elif isinstance(features, MorphAnalysis):
            self.morph = features
        else:
            if isinstance(features, int):
                features = self.vocab.strings[features]
            key = self.vocab.morphology.add(features)
            self.c.morph = key

    @property
    def lex(self):
        """RETURNS (Lexeme): The underlying lexeme."""
        return self.vocab[self.c.lex.orth]

    @property
    def lex_id(self):
        """RETURNS (int): Sequential ID of the token's lexical type."""
        return self.c.lex.id

    @property
    def rank(self):
        """RETURNS (int): Sequential ID of the token's lexical type, used to
        index into tables, e.g. for word vectors."""
        return self.c.lex.id

    @property
    def text(self):
        """RETURNS (str): The original verbatim text of the token."""
        return self.orth_

    @property
    def text_with_ws(self):
        """RETURNS (str): The text content of the span (with trailing
            whitespace).
        """
        cdef unicode orth = self.vocab.strings[self.c.lex.orth]
        if self.c.spacy:
            return orth + " "
        else:
            return orth

    @property
    def prob(self):
        """RETURNS (float): Smoothed log probability estimate of token type."""
        return self.vocab[self.c.lex.orth].prob

    @property
    def sentiment(self):
        """RETURNS (float): A scalar value indicating the positivity or
            negativity of the token."""
        if "sentiment" in self.doc.user_token_hooks:
            return self.doc.user_token_hooks["sentiment"](self)
        return self.vocab[self.c.lex.orth].sentiment

    @property
    def lang(self):
        """RETURNS (uint64): ID of the language of the parent document's
            vocabulary.
        """
        return self.c.lex.lang

    @property
    def idx(self):
        """RETURNS (int): The character offset of the token within the parent
            document.
        """
        return self.c.idx

    @property
    def cluster(self):
        """RETURNS (int): Brown cluster ID."""
        return self.vocab[self.c.lex.orth].cluster

    @property
    def orth(self):
        """RETURNS (uint64): ID of the verbatim text content."""
        return self.c.lex.orth

    @property
    def lower(self):
        """RETURNS (uint64): ID of the lowercase token text."""
        return self.c.lex.lower

    @property
    def norm(self):
        """RETURNS (uint64): ID of the token's norm, i.e. a normalised form of
            the token text. Usually set in the language's tokenizer exceptions
            or norm exceptions.
        """
        if self.c.norm == 0:
            return self.c.lex.norm
        else:
            return self.c.norm

    @property
    def shape(self):
        """RETURNS (uint64): ID of the token's shape, a transform of the
            token's string, to show orthographic features (e.g. "Xxxx", "dd").
        """
        return self.c.lex.shape

    @property
    def prefix(self):
        """RETURNS (uint64): ID of a length-N substring from the start of the
            token. Defaults to `N=1`.
        """
        return self.c.lex.prefix

    @property
    def suffix(self):
        """RETURNS (uint64): ID of a length-N substring from the end of the
            token. Defaults to `N=3`.
        """
        return self.c.lex.suffix

    property lemma:
        """RETURNS (uint64): ID of the base form of the word, with no
            inflectional suffixes.
        """
        def __get__(self):
            return self.c.lemma

        def __set__(self, attr_t lemma):
            self.c.lemma = lemma

    property pos:
        """RETURNS (uint64): ID of coarse-grained part-of-speech tag."""
        def __get__(self):
            return self.c.pos

        def __set__(self, pos):
            self.c.pos = pos

    property tag:
        """RETURNS (uint64): ID of fine-grained part-of-speech tag."""
        def __get__(self):
            return self.c.tag

        def __set__(self, attr_t tag):
            self.c.tag = tag

    property dep:
        """RETURNS (uint64): ID of syntactic dependency label."""
        def __get__(self):
            return self.c.dep

        def __set__(self, attr_t label):
            self.c.dep = label

    @property
    def has_vector(self):
        """A boolean value indicating whether a word vector is associated with
        the object.

        RETURNS (bool): Whether a word vector is associated with the object.

        DOCS: https://spacy.io/api/token#has_vector
        """
        if "has_vector" in self.doc.user_token_hooks:
            return self.doc.user_token_hooks["has_vector"](self)
        if self.vocab.vectors.size == 0 and self.doc.tensor.size != 0:
            return True
        return self.vocab.has_vector(self.c.lex.orth)

    @property
    def vector(self):
        """A real-valued meaning representation.

        RETURNS (numpy.ndarray[ndim=1, dtype='float32']): A 1D numpy array
            representing the token's semantics.

        DOCS: https://spacy.io/api/token#vector
        """
        if "vector" in self.doc.user_token_hooks:
            return self.doc.user_token_hooks["vector"](self)
        if self.vocab.vectors.size == 0 and self.doc.tensor.size != 0:
            return self.doc.tensor[self.i]
        else:
            return self.vocab.get_vector(self.c.lex.orth)

    @property
    def vector_norm(self):
        """The L2 norm of the token's vector representation.

        RETURNS (float): The L2 norm of the vector representation.

        DOCS: https://spacy.io/api/token#vector_norm
        """
        if "vector_norm" in self.doc.user_token_hooks:
            return self.doc.user_token_hooks["vector_norm"](self)
        vector = self.vector
        xp = get_array_module(vector)
        total = (vector ** 2).sum()
        return xp.sqrt(total) if total != 0. else 0.

    @property
    def tensor(self):
        if self.doc.tensor is None:
            return None
        return self.doc.tensor[self.i]

    @property
    def n_lefts(self):
        """The number of leftward immediate children of the word, in the
        syntactic dependency parse.

        RETURNS (int): The number of leftward immediate children of the
            word, in the syntactic dependency parse.

        DOCS: https://spacy.io/api/token#n_lefts
        """
        return self.c.l_kids

    @property
    def n_rights(self):
        """The number of rightward immediate children of the word, in the
        syntactic dependency parse.

        RETURNS (int): The number of rightward immediate children of the
            word, in the syntactic dependency parse.

        DOCS: https://spacy.io/api/token#n_rights
        """
        return self.c.r_kids

    @property
    def sent(self):
        """RETURNS (Span): The sentence span that the token is a part of."""
        if 'sent' in self.doc.user_token_hooks:
            return self.doc.user_token_hooks["sent"](self)
        return self.doc[self.i : self.i+1].sent

    property sent_start:
        def __get__(self):
            """Deprecated: use Token.is_sent_start instead."""
            # Raising a deprecation warning here causes errors for autocomplete
            # Handle broken backwards compatibility case: doc[0].sent_start
            # was False.
            if self.i == 0:
                return False
            else:
                return self.c.sent_start

        def __set__(self, value):
            self.is_sent_start = value

    property is_sent_start:
        """A boolean value indicating whether the token starts a sentence.
        `None` if unknown. Defaults to `True` for the first token in the `Doc`.

        RETURNS (bool / None): Whether the token starts a sentence.
            None if unknown.

        DOCS: https://spacy.io/api/token#is_sent_start
        """
        def __get__(self):
            if self.c.sent_start == 0:
                return None
            elif self.c.sent_start < 0:
                return False
            else:
                return True

        def __set__(self, value):
            if self.doc.has_annotation("DEP"):
                raise ValueError(Errors.E043)
            if value is None:
                self.c.sent_start = 0
            elif value is True:
                self.c.sent_start = 1
            elif value is False:
                self.c.sent_start = -1
            else:
                raise ValueError(Errors.E044.format(value=value))

    property is_sent_end:
        """A boolean value indicating whether the token ends a sentence.
        `None` if unknown. Defaults to `True` for the last token in the `Doc`.

        RETURNS (bool / None): Whether the token ends a sentence.
            None if unknown.

        DOCS: https://spacy.io/api/token#is_sent_end
        """
        def __get__(self):
            if self.i + 1 == len(self.doc):
                return True
            elif self.doc[self.i+1].is_sent_start == None:
                return None
            elif self.doc[self.i+1].is_sent_start == True:
                return True
            else:
                return False

        def __set__(self, value):
            raise ValueError(Errors.E196)

    @property
    def lefts(self):
        """The leftward immediate children of the word, in the syntactic
        dependency parse.

        YIELDS (Token): A left-child of the token.

        DOCS: https://spacy.io/api/token#lefts
        """
        cdef int nr_iter = 0
        cdef const TokenC* ptr = self.c - (self.i - self.c.l_edge)
        while ptr < self.c:
            if ptr + ptr.head == self.c:
                yield self.doc[ptr - (self.c - self.i)]
            ptr += 1
            nr_iter += 1
            # This is ugly, but it's a way to guard out infinite loops
            if nr_iter >= 10000000:
                raise RuntimeError(Errors.E045.format(attr="token.lefts"))

    @property
    def rights(self):
        """The rightward immediate children of the word, in the syntactic
        dependency parse.

        YIELDS (Token): A right-child of the token.

        DOCS: https://spacy.io/api/token#rights
        """
        cdef const TokenC* ptr = self.c + (self.c.r_edge - self.i)
        tokens = []
        cdef int nr_iter = 0
        while ptr > self.c:
            if ptr + ptr.head == self.c:
                tokens.append(self.doc[ptr - (self.c - self.i)])
            ptr -= 1
            nr_iter += 1
            if nr_iter >= 10000000:
                raise RuntimeError(Errors.E045.format(attr="token.rights"))
        tokens.reverse()
        for t in tokens:
            yield t

    @property
    def children(self):
        """A sequence of the token's immediate syntactic children.

        YIELDS (Token): A child token such that `child.head==self`.

        DOCS: https://spacy.io/api/token#children
        """
        yield from self.lefts
        yield from self.rights

    @property
    def subtree(self):
        """A sequence containing the token and all the token's syntactic
        descendants.

        YIELDS (Token): A descendent token such that
            `self.is_ancestor(descendent) or token == self`.

        DOCS: https://spacy.io/api/token#subtree
        """
        for word in self.lefts:
            yield from word.subtree
        yield self
        for word in self.rights:
            yield from word.subtree

    @property
    def left_edge(self) -> int:
        """The leftmost token of this token's syntactic descendents.

        RETURNS (Token): The first token such that `self.is_ancestor(token)`.
        """
        return self.doc[self.c.l_edge]

    @property
    def right_edge(self) -> int:
        """The rightmost token of this token's syntactic descendents.

        RETURNS (Token): The last token such that `self.is_ancestor(token)`.
        """
        return self.doc[self.c.r_edge]

    @property
    def ancestors(self):
        """A sequence of this token's syntactic ancestors.

        YIELDS (Token): A sequence of ancestor tokens such that
            `ancestor.is_ancestor(self)`.

        DOCS: https://spacy.io/api/token#ancestors
        """
        cdef const TokenC* head_ptr = self.c
        # Guard against infinite loop, no token can have
        # more ancestors than tokens in the tree.
        cdef int i = 0
        while head_ptr.head != 0 and i < self.doc.length:
            head_ptr += head_ptr.head
            yield self.doc[head_ptr - (self.c - self.i)]
            i += 1

    def is_ancestor(self, descendant):
        """Check whether this token is a parent, grandparent, etc. of another
        in the dependency tree.

        descendant (Token): Another token.
        RETURNS (bool): Whether this token is the ancestor of the descendant.

        DOCS: https://spacy.io/api/token#is_ancestor
        """
        if self.doc is not descendant.doc:
            return False
        return any(ancestor.i == self.i for ancestor in descendant.ancestors)

    def has_head(self):
        """Check whether the token has annotated head information.
        Return False when the head annotation is unset/missing.

        RETURNS (bool): Whether the head annotation is valid or not.
        """
        return not Token.missing_head(self.c)

    property head:
        """The syntactic parent, or "governor", of this token.
        If token.has_head() is `False`, this method will return itself.

        RETURNS (Token): The token predicted by the parser to be the head of
            the current token.
        """
        def __get__(self):
            if not self.has_head():
                return self
            else:
                return self.doc[self.i + self.c.head]

        def __set__(self, Token new_head):
            # This function sets the head of self to new_head and updates the
            # counters for left/right dependents and left/right corner for the
            # new and the old head
            # Check that token is from the same document
            if self.doc != new_head.doc:
                raise ValueError(Errors.E191)
            # Do nothing if old head is new head
            if self.i + self.c.head == new_head.i:
                return
            # Find the widest l/r_edges of the roots of the two tokens involved
            # to limit the number of tokens for set_children_from_heads
            cdef Token self_root, new_head_root
            self_root = ([self] + list(self.ancestors))[-1]
            new_head_ancestors = list(new_head.ancestors)
            new_head_root = new_head_ancestors[-1] if new_head_ancestors else new_head
            start = self_root.c.l_edge if self_root.c.l_edge < new_head_root.c.l_edge else new_head_root.c.l_edge
            end = self_root.c.r_edge if self_root.c.r_edge > new_head_root.c.r_edge else new_head_root.c.r_edge
            # Set new head
            self.c.head = new_head.i - self.i
            # Adjust parse properties and sentence starts
            set_children_from_heads(self.doc.c, start, end + 1)

    @property
    def conjuncts(self):
        """A sequence of coordinated tokens, including the token itself.

        RETURNS (tuple): The coordinated tokens.

        DOCS: https://spacy.io/api/token#conjuncts
        """
        cdef Token word, child
        if "conjuncts" in self.doc.user_token_hooks:
            return tuple(self.doc.user_token_hooks["conjuncts"](self))
        start = self
        while start.i != start.head.i:
            if start.dep == conj:
                start = start.head
            else:
                break
        queue = [start]
        output = [start]
        for word in queue:
            for child in word.rights:
                if child.c.dep == conj:
                    output.append(child)
                    queue.append(child)
        return tuple([w for w in output if w.i != self.i])

    property ent_type:
        """RETURNS (uint64): Named entity type."""
        def __get__(self):
            return self.c.ent_type

        def __set__(self, ent_type):
            self.c.ent_type = ent_type

    property ent_type_:
        """RETURNS (str): Named entity type."""
        def __get__(self):
            return self.vocab.strings[self.c.ent_type]

        def __set__(self, ent_type):
            self.c.ent_type = self.vocab.strings.add(ent_type)

    @property
    def ent_iob(self):
        """IOB code of named entity tag. `1="I", 2="O", 3="B"`. 0 means no tag
        is assigned.

        RETURNS (uint64): IOB code of named entity tag.
        """
        return self.c.ent_iob

    @classmethod
    def iob_strings(cls):
        return ("", "I", "O", "B")

    @property
    def ent_iob_(self):
        """IOB code of named entity tag. "B" means the token begins an entity,
        "I" means it is inside an entity, "O" means it is outside an entity,
        and "" means no entity tag is set. "B" with an empty ent_type
        means that the token is blocked from further processing by NER.

        RETURNS (str): IOB code of named entity tag.
        """
        return self.iob_strings()[self.c.ent_iob]

    property ent_id:
        """RETURNS (uint64): ID of the entity the token is an instance of,
            if any.
        """
        def __get__(self):
            return self.c.ent_id

        def __set__(self, hash_t key):
            self.c.ent_id = key

    property ent_id_:
        """RETURNS (str): ID of the entity the token is an instance of,
            if any.
        """
        def __get__(self):
            return self.vocab.strings[self.c.ent_id]

        def __set__(self, name):
            self.c.ent_id = self.vocab.strings.add(name)

    property ent_kb_id:
        """RETURNS (uint64): Named entity KB ID."""
        def __get__(self):
            return self.c.ent_kb_id

        def __set__(self, attr_t ent_kb_id):
            self.c.ent_kb_id = ent_kb_id

    property ent_kb_id_:
        """RETURNS (str): Named entity KB ID."""
        def __get__(self):
            return self.vocab.strings[self.c.ent_kb_id]

        def __set__(self, ent_kb_id):
            self.c.ent_kb_id = self.vocab.strings.add(ent_kb_id)

    @property
    def whitespace_(self):
        """RETURNS (str): The trailing whitespace character, if present."""
        return " " if self.c.spacy else ""

    @property
    def orth_(self):
        """RETURNS (str): Verbatim text content (identical to
            `Token.text`). Exists mostly for consistency with the other
            attributes.
        """
        return self.vocab.strings[self.c.lex.orth]

    @property
    def lower_(self):
        """RETURNS (str): The lowercase token text. Equivalent to
            `Token.text.lower()`.
        """
        return self.vocab.strings[self.c.lex.lower]

    property norm_:
        """RETURNS (str): The token's norm, i.e. a normalised form of the
            token text. Usually set in the language's tokenizer exceptions or
            norm exceptions.
        """
        def __get__(self):
            return self.vocab.strings[self.norm]

        def __set__(self, unicode norm_):
            self.c.norm = self.vocab.strings.add(norm_)

    @property
    def shape_(self):
        """RETURNS (str): Transform of the token's string, to show
            orthographic features. For example, "Xxxx" or "dd".
        """
        return self.vocab.strings[self.c.lex.shape]

    @property
    def prefix_(self):
        """RETURNS (str): A length-N substring from the start of the token.
            Defaults to `N=1`.
        """
        return self.vocab.strings[self.c.lex.prefix]

    @property
    def suffix_(self):
        """RETURNS (str): A length-N substring from the end of the token.
            Defaults to `N=3`.
        """
        return self.vocab.strings[self.c.lex.suffix]

    @property
    def lang_(self):
        """RETURNS (str): Language of the parent document's vocabulary,
            e.g. 'en'.
        """
        return self.vocab.strings[self.c.lex.lang]

    property lemma_:
        """RETURNS (str): The token lemma, i.e. the base form of the word,
            with no inflectional suffixes.
        """
        def __get__(self):
            return self.vocab.strings[self.c.lemma]

        def __set__(self, unicode lemma_):
            self.c.lemma = self.vocab.strings.add(lemma_)

    property pos_:
        """RETURNS (str): Coarse-grained part-of-speech tag."""
        def __get__(self):
            return parts_of_speech.NAMES[self.c.pos]

        def __set__(self, pos_name):
            if pos_name not in parts_of_speech.IDS:
                raise ValueError(Errors.E1021.format(pp=pos_name))
            self.c.pos = parts_of_speech.IDS[pos_name]

    property tag_:
        """RETURNS (str): Fine-grained part-of-speech tag."""
        def __get__(self):
            return self.vocab.strings[self.c.tag]

        def __set__(self, tag):
            self.tag = self.vocab.strings.add(tag)

    def has_dep(self):
        """Check whether the token has annotated dep information.
        Returns False when the dep label is unset/missing.

        RETURNS (bool): Whether the dep label is valid or not.
        """
        return not Token.missing_dep(self.c)

    property dep_:
        """RETURNS (str): The syntactic dependency label."""
        def __get__(self):
            return self.vocab.strings[self.c.dep]

        def __set__(self, unicode label):
            self.c.dep = self.vocab.strings.add(label)

    @property
    def is_oov(self):
        """RETURNS (bool): Whether the token is out-of-vocabulary."""
        return self.c.lex.orth not in self.vocab.vectors

    @property
    def is_stop(self):
        """RETURNS (bool): Whether the token is a stop word, i.e. part of a
            "stop list" defined by the language data.
        """
        return Lexeme.c_check_flag(self.c.lex, IS_STOP)

    @property
    def is_alpha(self):
        """RETURNS (bool): Whether the token consists of alpha characters.
            Equivalent to `token.text.isalpha()`.
        """
        return Lexeme.c_check_flag(self.c.lex, IS_ALPHA)

    @property
    def is_ascii(self):
        """RETURNS (bool): Whether the token consists of ASCII characters.
            Equivalent to `[any(ord(c) >= 128 for c in token.text)]`.
        """
        return Lexeme.c_check_flag(self.c.lex, IS_ASCII)

    @property
    def is_digit(self):
        """RETURNS (bool): Whether the token consists of digits. Equivalent to
            `token.text.isdigit()`.
        """
        return Lexeme.c_check_flag(self.c.lex, IS_DIGIT)

    @property
    def is_lower(self):
        """RETURNS (bool): Whether the token is in lowercase. Equivalent to
            `token.text.islower()`.
        """
        return Lexeme.c_check_flag(self.c.lex, IS_LOWER)

    @property
    def is_upper(self):
        """RETURNS (bool): Whether the token is in uppercase. Equivalent to
            `token.text.isupper()`
        """
        return Lexeme.c_check_flag(self.c.lex, IS_UPPER)

    @property
    def is_title(self):
        """RETURNS (bool): Whether the token is in titlecase. Equivalent to
            `token.text.istitle()`.
        """
        return Lexeme.c_check_flag(self.c.lex, IS_TITLE)

    @property
    def is_punct(self):
        """RETURNS (bool): Whether the token is punctuation."""
        return Lexeme.c_check_flag(self.c.lex, IS_PUNCT)

    @property
    def is_space(self):
        """RETURNS (bool): Whether the token consists of whitespace characters.
            Equivalent to `token.text.isspace()`.
        """
        return Lexeme.c_check_flag(self.c.lex, IS_SPACE)

    @property
    def is_bracket(self):
        """RETURNS (bool): Whether the token is a bracket."""
        return Lexeme.c_check_flag(self.c.lex, IS_BRACKET)

    @property
    def is_quote(self):
        """RETURNS (bool): Whether the token is a quotation mark."""
        return Lexeme.c_check_flag(self.c.lex, IS_QUOTE)

    @property
    def is_left_punct(self):
        """RETURNS (bool): Whether the token is a left punctuation mark."""
        return Lexeme.c_check_flag(self.c.lex, IS_LEFT_PUNCT)

    @property
    def is_right_punct(self):
        """RETURNS (bool): Whether the token is a right punctuation mark."""
        return Lexeme.c_check_flag(self.c.lex, IS_RIGHT_PUNCT)

    @property
    def is_currency(self):
        """RETURNS (bool): Whether the token is a currency symbol."""
        return Lexeme.c_check_flag(self.c.lex, IS_CURRENCY)

    @property
    def like_url(self):
        """RETURNS (bool): Whether the token resembles a URL."""
        return Lexeme.c_check_flag(self.c.lex, LIKE_URL)

    @property
    def like_num(self):
        """RETURNS (bool): Whether the token resembles a number, e.g. "10.9",
            "10", "ten", etc.
        """
        return Lexeme.c_check_flag(self.c.lex, LIKE_NUM)

    @property
    def like_email(self):
        """RETURNS (bool): Whether the token resembles an email address."""
        return Lexeme.c_check_flag(self.c.lex, LIKE_EMAIL)
