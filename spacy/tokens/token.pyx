from libc.string cimport memcpy
from cpython.mem cimport PyMem_Malloc, PyMem_Free
# Compiler crashes on memory view coercion without this. Should report bug.
from cython.view cimport array as cvarray
cimport numpy as np
np.import_array()

import numpy


from ..lexeme cimport Lexeme
from ..parts_of_speech import UNIV_POS_NAMES

from ..attrs cimport LEMMA
from ..attrs cimport ID, ORTH, NORM, LOWER, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER
from ..attrs cimport POS, LEMMA, TAG, DEP
from ..parts_of_speech cimport CONJ, PUNCT

from ..attrs cimport IS_ALPHA, IS_ASCII, IS_DIGIT, IS_LOWER, IS_PUNCT, IS_SPACE
from ..attrs cimport IS_TITLE, IS_UPPER, LIKE_URL, LIKE_NUM, LIKE_EMAIL, IS_STOP
from ..attrs cimport IS_OOV


cdef class Token:
    """An individual token --- i.e. a word, a punctuation symbol, etc.  Created
    via Doc.__getitem__ and Doc.__iter__.
    """
    def __cinit__(self, Vocab vocab, Doc doc, int offset):
        self.vocab = vocab
        self.doc = doc
        self.c = &self.doc.data[offset]
        self.i = offset
        self.array_len = doc.length

    def __len__(self):
        return self.c.lex.length

    def __unicode__(self):
        return self.string

    def __str__(self):
        return self.string

    cpdef bint check_flag(self, attr_id_t flag_id) except -1:
        return Lexeme.check_flag(self.c.lex, flag_id)

    def nbor(self, int i=1):
        return self.doc[self.i+i]

    property lex_id:
        def __get__(self):
            return self.c.lex.id

    property string:
        def __get__(self):
            cdef unicode orth = self.vocab.strings[self.c.lex.orth]
            if self.c.spacy:
                return orth + u' '
            else:
                return orth

    property prob:
        def __get__(self):
            return self.c.lex.prob

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

    property repvec:
        def __get__(self):
            cdef int length = self.vocab.repvec_length
            repvec_view = <float[:length,]>self.c.lex.repvec
            return numpy.asarray(repvec_view)

    property n_lefts:
        def __get__(self):
            cdef int n = 0
            cdef const TokenC* ptr = self.c - self.i
            while ptr != self.c:
                if ptr + ptr.head == self.c:
                    n += 1
                ptr += 1
            return n

    property n_rights:
        def __get__(self):
            cdef int n = 0
            cdef const TokenC* ptr = self.c + (self.array_len - self.i)
            while ptr != self.c:
                if ptr + ptr.head == self.c:
                    n += 1
                ptr -= 1
            return n

    property lefts:
        def __get__(self):
            """The leftward immediate children of the word, in the syntactic
            dependency parse.
            """
            cdef const TokenC* ptr = self.c - (self.i - self.c.l_edge)
            while ptr < self.c:
                # If this head is still to the right of us, we can skip to it
                # No token that's between this token and this head could be our
                # child.
                if (ptr.head >= 1) and (ptr + ptr.head) < self.c:
                    ptr += ptr.head

                elif ptr + ptr.head == self.c:
                    yield self.doc[ptr - (self.c - self.i)]
                    ptr += 1
                else:
                    ptr += 1

    property rights:
        def __get__(self):
            """The rightward immediate children of the word, in the syntactic
            dependency parse."""
            cdef const TokenC* ptr = self.c + (self.c.r_edge - self.i)
            tokens = []
            while ptr > self.c:
                # If this head is still to the right of us, we can skip to it
                # No token that's between this token and this head could be our
                # child.
                if (ptr.head < 0) and ((ptr + ptr.head) > self.c):
                    ptr += ptr.head
                elif ptr + ptr.head == self.c:
                    tokens.append(self.doc[ptr - (self.c - self.i)])
                    ptr -= 1
                else:
                    ptr -= 1
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

    property head:
        def __get__(self):
            """The token predicted by the parser to be the head of the current token."""
            return self.doc[self.i + self.c.head]

    property conjuncts:
        def __get__(self):
            """Get a list of conjoined words"""
            cdef Token word
            conjs = []
            if self.c.pos != CONJ and self.c.pos != PUNCT:
                seen_conj = False
                for word in reversed(list(self.lefts)):
                    if word.c.pos == CONJ:
                        seen_conj = True
                    elif seen_conj and word.c.pos == self.c.pos:
                        conjs.append(word)
            conjs.reverse()
            conjs.append(self)
            if seen_conj:
                return conjs
            elif self is not self.head and self in self.head.conjuncts:
                return self.head.conjuncts
            else:
                return []

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
            return self.string[self.c.lex.length:]

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

    property lemma_:
        def __get__(self):
            return self.vocab.strings[self.c.lemma]

    property pos_:
        def __get__(self):
            return _pos_id_to_string[self.c.pos]

    property tag_:
        def __get__(self):
            return self.vocab.strings[self.c.tag]

    property dep_:
        def __get__(self):
            return self.vocab.strings[self.c.dep]

    property is_oov:
        def __get__(self): return Lexeme.check_flag(self.c.lex, IS_OOV)

    property is_alpha:
        def __get__(self): return Lexeme.check_flag(self.c.lex, IS_ALPHA)

    property is_ascii:
        def __get__(self): return Lexeme.check_flag(self.c.lex, IS_ASCII)

    property is_digit:
        def __get__(self): return Lexeme.check_flag(self.c.lex, IS_DIGIT)

    property is_lower:
        def __get__(self): return Lexeme.check_flag(self.c.lex, IS_LOWER)

    property is_title:
        def __get__(self): return Lexeme.check_flag(self.c.lex, IS_TITLE)

    property is_punct:
        def __get__(self): return Lexeme.check_flag(self.c.lex, IS_PUNCT)

    property is_space: 
        def __get__(self): return Lexeme.check_flag(self.c.lex, IS_SPACE)

    property like_url:
        def __get__(self): return Lexeme.check_flag(self.c.lex, LIKE_URL)

    property like_num:
        def __get__(self): return Lexeme.check_flag(self.c.lex, LIKE_NUM)

    property like_email:
        def __get__(self): return Lexeme.check_flag(self.c.lex, LIKE_EMAIL)


_pos_id_to_string = {id_: string for string, id_ in UNIV_POS_NAMES.items()}
