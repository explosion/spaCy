from libc.string cimport memcpy
from cpython.mem cimport PyMem_Malloc, PyMem_Free
# Compiler crashes on memory view coercion without this. Should report bug.
from cython.view cimport array as cvarray
cimport numpy as np
np.import_array()

import numpy
import six


from ..lexeme cimport Lexeme
from .. import parts_of_speech

from ..attrs cimport LEMMA
from ..attrs cimport ID, ORTH, NORM, LOWER, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER
from ..attrs cimport POS, LEMMA, TAG, DEP
from ..parts_of_speech cimport CONJ, PUNCT

from ..attrs cimport IS_ALPHA, IS_ASCII, IS_DIGIT, IS_LOWER, IS_PUNCT, IS_SPACE
from ..attrs cimport IS_BRACKET
from ..attrs cimport IS_QUOTE
from ..attrs cimport IS_LEFT_PUNCT
from ..attrs cimport IS_RIGHT_PUNCT
from ..attrs cimport IS_TITLE, IS_UPPER, LIKE_URL, LIKE_NUM, LIKE_EMAIL, IS_STOP
from ..attrs cimport IS_OOV

from ..lexeme cimport Lexeme


_STR_TRAILING_WHITESPACE = False

def use_deprecated_Token__str__semantics(value):
    '''
    Preserve deprecated semantics for Token.__str__ and Token.__unicode__ methods.
    
    spaCy < 0.100.7 had a bug in the semantics of the Token.__str__ and Token.__unicode__
    built-ins: they included a trailing space. To ease the transition to the
    new semantics, you can use this function to switch the old semantics back on.
    
    Example:

        from spacy.tokens.token import keep_deprecated_Token.__str__semantics
        keep_deprecated_Token.__str__semantics(True)

    This function will not remain in future versions --- it's a temporary shim.
    '''
    global _STR_TRAILING_WHITESPACE
    _STR_TRAILING_WHITESPACE = value


cdef class Token:
    """An individual token --- i.e. a word, a punctuation symbol, etc.  Created
    via Doc.__getitem__ and Doc.__iter__.
    """
    def __cinit__(self, Vocab vocab, Doc doc, int offset):
        self.vocab = vocab
        self.doc = doc
        self.c = &self.doc.c[offset]
        self.i = offset
        self.array_len = doc.length

    def __len__(self):
        return self.c.lex.length

    def __unicode__(self):
        # Users can toggle this on to preserve former buggy semantics.
        # Remove this in future versions.
        if _STR_TRAILING_WHITESPACE:
            return self.text_with_ws
        else:
            return self.text

    def __bytes__(self):
        # Users can toggle this on to preserve former buggy semantics.
        # Remove this in future versions.
        if _STR_TRAILING_WHITESPACE:
            return self.text_with_ws.encode('utf8')
        else:
            return self.text.encode('utf8')

    def __str__(self):
        if six.PY3:
            return self.__unicode__()
        return self.__bytes__()

    def __repr__(self):
        return self.__str__()

    cpdef bint check_flag(self, attr_id_t flag_id) except -1:
        return Lexeme.c_check_flag(self.c.lex, flag_id)

    def nbor(self, int i=1):
        return self.doc[self.i+i]

    def similarity(self, other):
        if self.vector_norm == 0 or other.vector_norm == 0:
            return 0.0
        return numpy.dot(self.vector, other.vector) / (self.vector_norm * other.vector_norm)

    property lex_id:
        def __get__(self):
            return self.c.lex.id

    property rank:
        def __get__(self):
            return self.c.lex.id

    property string:
        def __get__(self):
            return self.text_with_ws

    property text:
        def __get__(self):
            return self.orth_

    property text_with_ws:
        def __get__(self):
            cdef unicode orth = self.vocab.strings[self.c.lex.orth]
            if self.c.spacy:
                return orth + u' '
            else:
                return orth

    property prob:
        def __get__(self):
            return self.c.lex.prob

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
        def __get__(self):
            return self.c.lemma

    property pos:
        def __get__(self):
            return self.c.pos

    property tag:
        def __get__(self):
            return self.c.tag

    property dep:
        def __get__(self):
            return self.c.dep
        def __set__(self, int label):
            self.c.dep = label

    property has_vector:
        def __get__(self):
            cdef int i
            for i in range(self.vocab.vectors_length):
                if self.c.lex.vector[i] != 0:
                    return True
            else:
                return False

    property vector:
        def __get__(self):
            cdef int length = self.vocab.vectors_length
            if length == 0:
                raise ValueError(
                    "Word vectors set to length 0. This may be because the "
                    "data is not installed. If you haven't already, run"
                    "\npython -m spacy.%s.download all\n"
                    "to install the data." % self.vocab.lang
                )
            vector_view = <float[:length,]>self.c.lex.vector
            return numpy.asarray(vector_view)

    property repvec:
        def __get__(self):
            return self.vector

    property vector_norm:
        def __get__(self):
            return self.c.lex.l2_norm

    property n_lefts:
        def __get__(self):
            return self.c.l_kids

    property n_rights:
        def __get__(self):
            return self.c.r_kids

    property lefts:
        def __get__(self):
            """The leftward immediate children of the word, in the syntactic
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
            """The rightward immediate children of the word, in the syntactic
            dependency parse."""
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
        def __get__(self):
            yield from self.lefts
            yield from self.rights

    property subtree:
        def __get__(self):
            for word in self.lefts:
                yield from word.subtree
            yield self
            for word in self.rights:
                yield from word.subtree

    property left_edge:
        def __get__(self):
            return self.doc[self.c.l_edge]

    property right_edge:
        def __get__(self):
            return self.doc[self.c.r_edge]

    property ancestors:
        def __get__(self):
            cdef const TokenC* head_ptr = self.c
            # guard against infinite loop, no token can have 
            # more ancestors than tokens in the tree
            cdef int i = 0
            while head_ptr.head != 0 and i < self.doc.length:
                head_ptr += head_ptr.head
                yield self.doc[head_ptr - (self.c - self.i)]
                i += 1

    def is_ancestor_of(self, descendant):
        return any( ancestor.i == self.i for ancestor in descendant.ancestors )

    property head:
        def __get__(self):
            """The token predicted by the parser to be the head of the current token."""
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
            cdef bint is_desc = old_head.is_ancestor_of(new_head)
            
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
        def __get__(self):
            """Get a list of conjoined words."""
            cdef Token word
            if self.dep_ != 'conj':
                for word in self.rights:
                    if word.dep_ == 'conj':
                        yield word
                        yield from word.conjuncts

    property ent_type:
        def __get__(self):
            return self.c.ent_type

    property ent_iob:
        def __get__(self):
            return self.c.ent_iob

    property ent_type_:
        def __get__(self):
            return self.vocab.strings[self.c.ent_type]

    property ent_iob_:
        def __get__(self):
            iob_strings = ('', 'I', 'O', 'B')
            return iob_strings[self.c.ent_iob]

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
        def __get__(self):
            return self.vocab.strings[self.c.lemma]

    property pos_:
        def __get__(self):
            return parts_of_speech.NAMES[self.c.pos]

    property tag_:
        def __get__(self):
            return self.vocab.strings[self.c.tag]

    property dep_:
        def __get__(self):
            return self.vocab.strings[self.c.dep]
        def __set__(self, unicode label):
            self.c.dep = self.vocab.strings[label]

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
