# cython: infer_types=True
# coding: utf8
from __future__ import unicode_literals

from libc.string cimport memcpy
from cpython.mem cimport PyMem_Malloc, PyMem_Free
# Compiler crashes on memory view coercion without this. Should report bug.
from cython.view cimport array as cvarray
cimport numpy as np
np.import_array()
import numpy

from ..typedefs cimport hash_t
from ..lexeme cimport Lexeme
from .. import parts_of_speech
from ..attrs cimport IS_ALPHA, IS_ASCII, IS_DIGIT, IS_LOWER, IS_PUNCT, IS_SPACE
from ..attrs cimport IS_BRACKET, IS_QUOTE, IS_LEFT_PUNCT, IS_RIGHT_PUNCT, IS_OOV
from ..attrs cimport IS_TITLE, IS_UPPER, LIKE_URL, LIKE_NUM, LIKE_EMAIL, IS_STOP
from ..attrs cimport ID, ORTH, NORM, LOWER, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER
from ..attrs cimport LEMMA, POS, TAG, DEP
from ..compat import is_config
from .. import about


cdef class Token:
    """An individual token – i.e. a word, punctuation symbol, whitespace, etc."""
    def __cinit__(self, Vocab vocab, Doc doc, int offset):
        """Construct a `Token` object.

        vocab (Vocab): A storage container for lexical types.
        doc (Doc): The parent document.
        offset (int): The index of the token within the document.
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
        """
        return self.c.lex.length

    def __unicode__(self):
        return self.text

    def __bytes__(self):
        return self.text.encode('utf8')

    def __str__(self):
        if is_config(python3=True):
            return self.__unicode__()
        return self.__bytes__()

    def __repr__(self):
        return self.__str__()

    def __richcmp__(self, Token other, int op):
        # http://cython.readthedocs.io/en/latest/src/userguide/special_methods.html
        cdef Doc my_doc = self.doc
        cdef Doc other_doc = other.doc
        my = self.idx
        their = other.idx if other is not None else None
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
            raise ValueError(op)

    cpdef bint check_flag(self, attr_id_t flag_id) except -1:
        """Check the value of a boolean flag.

        flag_id (int): The ID of the flag attribute.
        RETURNS (bool): Whether the flag is set.

        EXAMPLE:
            >>> from spacy.attrs import IS_TITLE
            >>> doc = nlp(u'Give it back! He pleaded.')
            >>> token = doc[0]
            >>> token.check_flag(IS_TITLE)
            True
        """
        return Lexeme.c_check_flag(self.c.lex, flag_id)

    def nbor(self, int i=1):
        """Get a neighboring token.

        i (int): The relative position of the token to get. Defaults to 1.
        RETURNS (Token): The token at position `self.doc[self.i+i]`.
        """
        return self.doc[self.i+i]

    def similarity(self, other):
        """Make a semantic similarity estimate. The default estimate is cosine
        similarity using an average of word vectors.

        other (object): The object to compare with. By default, accepts `Doc`,
            `Span`, `Token` and `Lexeme` objects.
        RETURNS (float): A scalar similarity score. Higher is more similar.
        """
        if 'similarity' in self.doc.user_token_hooks:
            return self.doc.user_token_hooks['similarity'](self)
        if self.vector_norm == 0 or other.vector_norm == 0:
            return 0.0
        return numpy.dot(self.vector, other.vector) / (self.vector_norm * other.vector_norm)

    property lex_id:
        """ID of the token's lexical type.

        RETURNS (int): ID of the token's lexical type."""
        def __get__(self):
            return self.c.lex.id

    property rank:
        # TODO: add docstring
        def __get__(self):
            return self.c.lex.id

    property string:
        def __get__(self):
            return self.text_with_ws

    property text:
        """A unicode representation of the token text.

        RETURNS (unicode): The original verbatim text of the token.
        """
        def __get__(self):
            return self.orth_

    property text_with_ws:
        """The text content of the token with a trailing whitespace character if
        it has one.

        RETURNS (unicode): The text content of the span (with trailing whitespace).
        """
        def __get__(self):
            cdef unicode orth = self.vocab.strings[self.c.lex.orth]
            if self.c.spacy:
                return orth + u' '
            else:
                return orth

    property prob:
        def __get__(self):
            return self.c.lex.prob

    property sentiment:
        def __get__(self):
            if 'sentiment' in self.doc.user_token_hooks:
                return self.doc.user_token_hooks['sentiment'](self)
            return self.c.lex.sentiment

    property lang:
        def __get__(self):
            return self.c.lex.lang

    property idx:
        def __get__(self):
            return self.c.idx

    property cluster:
        def __get__(self):
            return self.c.lex.cluster

    property orth:
        def __get__(self):
            return self.c.lex.orth

    property lower:
        def __get__(self):
            return self.c.lex.lower

    property norm:
        def __get__(self):
            return self.c.lex.norm

    property shape:
        def __get__(self):
            return self.c.lex.shape

    property prefix:
        def __get__(self):
            return self.c.lex.prefix

    property suffix:
        def __get__(self):
            return self.c.lex.suffix

    property lemma:
        """Base form of the word, with no inflectional suffixes.

        RETURNS (uint64): Token lemma.
        """
        def __get__(self):
            return self.c.lemma
        def __set__(self, attr_t lemma):
            self.c.lemma = lemma

    property pos:
        def __get__(self):
            return self.c.pos

    property tag:
        def __get__(self):
            return self.c.tag
        def __set__(self, attr_t tag):
            self.vocab.morphology.assign_tag(self.c, tag)

    property dep:
        def __get__(self):
            return self.c.dep
        def __set__(self, attr_t label):
            self.c.dep = label

    property has_vector:
        """A boolean value indicating whether a word vector is associated with
        the object.

        RETURNS (bool): Whether a word vector is associated with the object.
        """
        def __get__(self):
            if 'has_vector' in self.doc.user_token_hooks:
                return self.doc.user_token_hooks['has_vector'](self)
            return self.vocab.has_vector(self.c.lex.orth)

    property vector:
        """A real-valued meaning representation.

        RETURNS (numpy.ndarray[ndim=1, dtype='float32']): A 1D numpy array
            representing the token's semantics.
        """
        def __get__(self):
            if 'vector' in self.doc.user_token_hooks:
                return self.doc.user_token_hooks['vector'](self)
            if self.has_vector:
                return self.vocab.get_vector(self.c.lex.orth)
            else:
                return self.doc.tensor[self.i]

    property vector_norm:
        """The L2 norm of the token's vector representation.

        RETURNS (float): The L2 norm of the vector representation.
        """
        def __get__(self):
            if 'vector_norm' in self.doc.user_token_hooks:
                return self.doc.user_token_hooks['vector_norm'](self)
            vector = self.vector 
            return numpy.sqrt((vector ** 2).sum())

    property n_lefts:
        def __get__(self):
            return self.c.l_kids

    property n_rights:
        def __get__(self):
            return self.c.r_kids

    property sent_start:
        def __get__(self):
            return self.c.sent_start

        def __set__(self, bint value):
            if self.doc.is_parsed:
                raise ValueError(
                    'Refusing to write to token.sent_start if its document is parsed, '
                    'because this may cause inconsistent state. '
                    'See https://github.com/spacy-io/spaCy/issues/235 for workarounds.')
            self.c.sent_start = value

    property lefts:
        def __get__(self):
            """
            The leftward immediate children of the word, in the syntactic
            dependency parse.
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
                    raise RuntimeError(
                        "Possibly infinite loop encountered while looking for token.lefts")

    property rights:
        def __get__(self):
            """
            The rightward immediate children of the word, in the syntactic
            dependency parse.
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
                    raise RuntimeError(
                        "Possibly infinite loop encountered while looking for token.rights")
            tokens.reverse()
            for t in tokens:
                yield t

    property children:
        """
        A sequence of the token's immediate syntactic children.

        Yields: Token A child token such that child.head==self
        """
        def __get__(self):
            yield from self.lefts
            yield from self.rights

    property subtree:
        """
        A sequence of all the token's syntactic descendents.

        Yields: Token A descendent token such that self.is_ancestor(descendent)
        """
        def __get__(self):
            for word in self.lefts:
                yield from word.subtree
            yield self
            for word in self.rights:
                yield from word.subtree

    property left_edge:
        """The leftmost token of this token's syntactic descendents.

        RETURNS (Token): The first token such that `self.is_ancestor(token)`.
        """
        def __get__(self):
            return self.doc[self.c.l_edge]

    property right_edge:
        """The rightmost token of this token's syntactic descendents.

        RETURNS (Token): The last token such that `self.is_ancestor(token)`.
        """
        def __get__(self):
            return self.doc[self.c.r_edge]

    property ancestors:
        """A sequence of this token's syntactic ancestors.

        YIELDS (Token): A sequence of ancestor tokens such that
            `ancestor.is_ancestor(self)`.
        """
        def __get__(self):
            cdef const TokenC* head_ptr = self.c
            # guard against infinite loop, no token can have
            # more ancestors than tokens in the tree
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
        """
        if self.doc is not descendant.doc:
            return False
        return any( ancestor.i == self.i for ancestor in descendant.ancestors )

    property head:
        """The syntactic parent, or "governor", of this token.

        RETURNS (Token): The token head.
        """
        def __get__(self):
            """The token predicted by the parser to be the head of the current
            token.
            """
            return self.doc[self.i + self.c.head]
        def __set__(self, Token new_head):
            # this function sets the head of self to new_head
            # and updates the counters for left/right dependents
            # and left/right corner for the new and the old head

            # do nothing if old head is new head
            if self.i + self.c.head == new_head.i:
                return

            cdef Token old_head = self.head
            cdef int rel_newhead_i = new_head.i - self.i

            # is the new head a descendant of the old head
            cdef bint is_desc = old_head.is_ancestor(new_head)

            cdef int new_edge
            cdef Token anc, child

            # update number of deps of old head
            if self.c.head > 0: # left dependent
                old_head.c.l_kids -= 1
                if self.c.l_edge == old_head.c.l_edge:
                    # the token dominates the left edge so the left edge of the head
                    # may change when the token is reattached
                    # it may not change if the new head is a descendant of the current head

                    new_edge = self.c.l_edge
                    # the new l_edge is the left-most l_edge on any of the other dependents
                    # where the l_edge is left of the head, otherwise it is the head
                    if not is_desc:
                        new_edge = old_head.i
                        for child in old_head.children:
                            if child == self:
                                continue
                            if child.c.l_edge < new_edge:
                                new_edge = child.c.l_edge
                        old_head.c.l_edge = new_edge

                    # walk up the tree from old_head and assign new l_edge to ancestors
                    # until an ancestor already has an l_edge that's further left
                    for anc in old_head.ancestors:
                        if anc.c.l_edge <= new_edge:
                            break
                        anc.c.l_edge = new_edge

            elif self.c.head < 0: # right dependent
                old_head.c.r_kids -= 1
                # do the same thing as for l_edge
                if self.c.r_edge == old_head.c.r_edge:
                    new_edge = self.c.r_edge

                    if not is_desc:
                        new_edge = old_head.i
                        for child in old_head.children:
                            if child == self:
                                continue
                            if child.c.r_edge > new_edge:
                                new_edge = child.c.r_edge
                        old_head.c.r_edge = new_edge

                    for anc in old_head.ancestors:
                        if anc.c.r_edge >= new_edge:
                            break
                        anc.c.r_edge = new_edge

            # update number of deps of new head
            if rel_newhead_i > 0: # left dependent
                new_head.c.l_kids += 1
                # walk up the tree from new head and set l_edge to self.l_edge
                # until you hit a token with an l_edge further to the left
                if self.c.l_edge < new_head.c.l_edge:
                    new_head.c.l_edge = self.c.l_edge
                    for anc in new_head.ancestors:
                        if anc.c.l_edge <= self.c.l_edge:
                            break
                        anc.c.l_edge = self.c.l_edge

            elif rel_newhead_i < 0: # right dependent
                new_head.c.r_kids += 1
                # do the same as for l_edge
                if self.c.r_edge > new_head.c.r_edge:
                    new_head.c.r_edge = self.c.r_edge
                    for anc in new_head.ancestors:
                        if anc.c.r_edge >= self.c.r_edge:
                            break
                        anc.c.r_edge = self.c.r_edge

            # set new head
            self.c.head = rel_newhead_i

    property conjuncts:
        """A sequence of coordinated tokens, including the token itself.

        YIELDS (Token): A coordinated token.
        """
        def __get__(self):
            """Get a list of conjoined words."""
            cdef Token word
            if 'conjuncts' in self.doc.user_token_hooks:
                yield from self.doc.user_token_hooks['conjuncts'](self)
            else:
                if self.dep_ != 'conj':
                    for word in self.rights:
                        if word.dep_ == 'conj':
                            yield word
                            yield from word.conjuncts

    property ent_type:
        """Named entity type.

        RETURNS (uint64): Named entity type.
        """
        def __get__(self):
            return self.c.ent_type
        def __set__(self, ent_type):
            self.c.ent_type = ent_type

    property ent_iob:
        """IOB code of named entity tag. `1="I", 2="O", 3="B"`. 0 means no tag
        is assigned.

        RETURNS (uint64): IOB code of named entity tag.
        """
        def __get__(self):
            return self.c.ent_iob

    property ent_type_:
        """Named entity type.

        RETURNS (unicode): Named entity type.
        """
        def __get__(self):
            return self.vocab.strings[self.c.ent_type]
        def __set__(self, ent_type):
            self.c.ent_type = self.vocab.strings.add(ent_type)

    property ent_iob_:
        """IOB code of named entity tag. "B" means the token begins an entity,
        "I" means it is inside an entity, "O" means it is outside an entity, and
        "" means no entity tag is set.

        RETURNS (unicode): IOB code of named entity tag.
        """
        def __get__(self):
            iob_strings = ('', 'I', 'O', 'B')
            return iob_strings[self.c.ent_iob]

    property ent_id:
        """ID of the entity the token is an instance of, if any. Usually
        assigned by patterns in the Matcher.

        RETURNS (uint64): ID of the entity.
        """
        def __get__(self):
            return self.c.ent_id

        def __set__(self, hash_t key):
            self.c.ent_id = key

    property ent_id_:
        """ID of the entity the token is an instance of, if any. Usually
        assigned by patterns in the Matcher.

        RETURNS (unicode): ID of the entity.
        """
        def __get__(self):
            return self.vocab.strings[self.c.ent_id]

        def __set__(self, name):
            self.c.ent_id = self.vocab.strings.add(name)

    property whitespace_:
        def __get__(self):
            return ' ' if self.c.spacy else ''

    property orth_:
        def __get__(self):
            return self.vocab.strings[self.c.lex.orth]

    property lower_:
        def __get__(self):
            return self.vocab.strings[self.c.lex.lower]

    property norm_:
        def __get__(self):
            return self.vocab.strings[self.c.lex.norm]

    property shape_:
        def __get__(self):
            return self.vocab.strings[self.c.lex.shape]

    property prefix_:
        def __get__(self):
            return self.vocab.strings[self.c.lex.prefix]

    property suffix_:
        def __get__(self):
            return self.vocab.strings[self.c.lex.suffix]

    property lang_:
        def __get__(self):
            return self.vocab.strings[self.c.lex.lang]

    property lemma_:
        """Base form of the word, with no inflectional suffixes.

        RETURNS (unicode): Token lemma.
        """
        def __get__(self):
            return self.vocab.strings[self.c.lemma]
        def __set__(self, unicode lemma_):
            self.c.lemma = self.vocab.strings.add(lemma_)

    property pos_:
        def __get__(self):
            return parts_of_speech.NAMES[self.c.pos]

    property tag_:
        def __get__(self):
            return self.vocab.strings[self.c.tag]
        def __set__(self, tag):
            self.tag = self.vocab.strings.add(tag)

    property dep_:
        def __get__(self):
            return self.vocab.strings[self.c.dep]
        def __set__(self, unicode label):
            self.c.dep = self.vocab.strings.add(label)

    property is_oov:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_OOV)

    property is_stop:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_STOP)

    property is_alpha:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_ALPHA)

    property is_ascii:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_ASCII)

    property is_digit:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_DIGIT)

    property is_lower:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_LOWER)

    property is_title:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_TITLE)

    property is_punct:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_PUNCT)

    property is_space:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_SPACE)

    property is_bracket:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_BRACKET)

    property is_quote:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_QUOTE)

    property is_left_punct:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_LEFT_PUNCT)

    property is_right_punct:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, IS_RIGHT_PUNCT)

    property like_url:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, LIKE_URL)

    property like_num:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, LIKE_NUM)

    property like_email:
        def __get__(self): return Lexeme.c_check_flag(self.c.lex, LIKE_EMAIL)
