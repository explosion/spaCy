# cython: embedsignature=True
from libc.string cimport memset

from preshed.maps cimport PreshMap
from preshed.counter cimport PreshCounter

from .strings cimport slice_unicode
from .vocab cimport EMPTY_LEXEME
from .typedefs cimport attr_id_t, attr_t
from .typedefs cimport LEMMA
from .typedefs cimport ID, ORTH, NORM, LOWER, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER
from .typedefs cimport POS, LEMMA
from .parts_of_speech import UNIV_POS_NAMES
from .lexeme cimport check_flag
from .spans import Span
from .structs cimport UniStr

from unidecode import unidecode

cimport numpy
import numpy

cimport cython

from cpython.mem cimport PyMem_Malloc, PyMem_Free
from libc.string cimport memcpy

DEF PADDING = 5


cdef int bounds_check(int i, int length, int padding) except -1:
    if (i + padding) < 0:
        raise IndexError
    if (i - padding) >= length:
        raise IndexError


cdef attr_t get_token_attr(const TokenC* token, attr_id_t feat_name) nogil:
    if feat_name == LEMMA:
        return token.lemma
    elif feat_name == POS:
        return token.pos
    else:
        return get_lex_attr(token.lex, feat_name)


cdef attr_t get_lex_attr(const LexemeC* lex, attr_id_t feat_name) nogil:
    if feat_name < (sizeof(flags_t) * 8):
        return check_flag(lex, feat_name)
    elif feat_name == ID:
        return lex.id
    elif feat_name == ORTH:
        return lex.orth
    elif feat_name == LOWER:
        return lex.lower
    elif feat_name == NORM:
        return lex.norm
    elif feat_name == SHAPE:
        return lex.shape
    elif feat_name == PREFIX:
        return lex.prefix
    elif feat_name == SUFFIX:
        return lex.suffix
    elif feat_name == LENGTH:
        return lex.length
    elif feat_name == CLUSTER:
        return lex.cluster
    else:
        return 0


cdef class Tokens:
    """
    Container class for annotated text.  Constructed via English.__call__ or
    Tokenizer.__call__.
    """
    def __cinit__(self, Vocab vocab, unicode string):
        self.vocab = vocab
        self._string = string
        string_length = len(string)
        if string_length >= 3:
            size = int(string_length / 3.0)
        else:
            size = 5
        self.mem = Pool()
        # Guarantee self.lex[i-x], for any i >= 0 and x < padding is in bounds
        # However, we need to remember the true starting places, so that we can
        # realloc.
        data_start = <TokenC*>self.mem.alloc(size + (PADDING*2), sizeof(TokenC))
        cdef int i
        for i in range(size + (PADDING*2)):
            data_start[i].lex = &EMPTY_LEXEME
        self.data = data_start + PADDING
        self.max_length = size
        self.length = 0
        self.is_tagged = False
        self.is_parsed = False
        self._py_tokens = []

    def __getitem__(self, object i):
        """Retrieve a token.
        
        The Python Token objects are created lazily from internal C data, and
        cached in _py_tokens
        
        Returns:
            token (Token):
        """
        if i < 0:
            i = self.length + i
        bounds_check(i, self.length, PADDING)
        return Token.cinit(self.vocab, self._string,
                           &self.data[i], i, self.length,
                           self)

    def __iter__(self):
        """Iterate over the tokens.

        Yields:
            token (Token):
        """
        for i in range(self.length):
            yield Token.cinit(self.vocab, self._string,
                              &self.data[i], i, self.length,
                              self)

    def __len__(self):
        return self.length

    def __unicode__(self):
        cdef const TokenC* last = &self.data[self.length - 1]
        return self._string[:last.idx + last.lex.length]

    property ents:
        def __get__(self):
            cdef int i
            cdef const TokenC* token
            cdef int start = -1
            cdef int label = 0
            for i in range(self.length):
                token = &self.data[i]
                if token.ent_iob == 1:
                    assert start != -1
                    pass
                elif token.ent_iob == 2:
                    if start != -1:
                         yield Span(self, start, i, label=label)
                    start = -1
                    label = 0
                elif token.ent_iob == 3:
                    start = i
                    label = token.ent_type
            if start != -1:
                yield Span(self, start, self.length, label=label)

    cdef int push_back(self, int idx, LexemeOrToken lex_or_tok) except -1:
        if self.length == self.max_length:
            self._realloc(self.length * 2)
        cdef TokenC* t = &self.data[self.length]
        if LexemeOrToken is TokenC_ptr:
            t[0] = lex_or_tok[0]
        else:
            t.lex = lex_or_tok
        t.idx = idx
        self.length += 1
        self._py_tokens.append(None)
        return idx + t.lex.length

    @cython.boundscheck(False)
    cpdef long[:,:] to_array(self, object py_attr_ids):
        """Given a list of M attribute IDs, export the tokens to a numpy ndarray
        of shape N*M, where N is the length of the sentence.

        Arguments:
            attr_ids (list[int]): A list of attribute ID ints.

        Returns:
            feat_array (numpy.ndarray[long, ndim=2]):
              A feature matrix, with one row per word, and one column per attribute
              indicated in the input attr_ids.
        """
        cdef int i, j
        cdef attr_id_t feature
        cdef numpy.ndarray[long, ndim=2] output
        # Make an array from the attributes --- otherwise our inner loop is Python
        # dict iteration.
        cdef numpy.ndarray[long, ndim=1] attr_ids = numpy.asarray(py_attr_ids)
        output = numpy.ndarray(shape=(self.length, len(attr_ids)), dtype=numpy.int)
        for i in range(self.length):
            for j, feature in enumerate(attr_ids):
                output[i, j] = get_token_attr(&self.data[i], feature)
        return output

    def count_by(self, attr_id_t attr_id, exclude=None):
        """Produce a dict of {attribute (int): count (ints)} frequencies, keyed
        by the values of the given attribute ID.

          >>> from spacy.en import English, attrs
          >>> nlp = English()
          >>> tokens = nlp(u'apple apple orange banana')
          >>> tokens.count_by(attrs.ORTH)
          {12800L: 1, 11880L: 2, 7561L: 1}
          >>> tokens.to_array([attrs.ORTH])
          array([[11880],
                 [11880],
                 [ 7561],
                 [12800]])
        """
        cdef int i
        cdef attr_t attr
        cdef size_t count

        cdef PreshCounter counts = PreshCounter(2 ** 8)
        for i in range(self.length):
            if exclude is not None and exclude(self[i]):
                continue
            attr = get_token_attr(&self.data[i], attr_id)
            counts.inc(attr, 1)
        return dict(counts)

    def _realloc(self, new_size):
        self.max_length = new_size
        n = new_size + (PADDING * 2)
        # What we're storing is a "padded" array. We've jumped forward PADDING
        # places, and are storing the pointer to that. This way, we can access
        # words out-of-bounds, and get out-of-bounds markers.
        # Now that we want to realloc, we need the address of the true start,
        # so we jump the pointer back PADDING places.
        cdef TokenC* data_start = self.data - PADDING
        data_start = <TokenC*>self.mem.realloc(data_start, n * sizeof(TokenC))
        self.data = data_start + PADDING
        cdef int i
        for i in range(self.length, self.max_length + PADDING):
            self.data[i].lex = &EMPTY_LEXEME

    @property
    def sents(self):
        """This is really only a place-holder for a proper solution."""
        cdef int i
        cdef Tokens sent = Tokens(self.vocab, self._string[self.data[0].idx:])
        start = None
        for i in range(self.length):
            if start is None:
                start = i
            if self.data[i].sent_end:
                yield Span(self, start, i+1)
                start = None
        if start is not None:
            yield Span(self, start, self.length) 

    cdef int set_parse(self, const TokenC* parsed) except -1:
        # TODO: This method is fairly misleading atm. It's used by GreedyParser
        # to actually apply the parse calculated. Need to rethink this.
        self._py_tokens = [None] * self.length
        self.is_parsed = True
        for i in range(self.length):
            self.data[i] = parsed[i]

    def merge(self, int start_idx, int end_idx, unicode tag, unicode lemma,
              unicode ent_type):
        cdef int i
        cdef int start = -1
        cdef int end = -1
        for i in range(self.length):
            if self.data[i].idx == start_idx:
                start = i
            if (self.data[i].idx + self.data[i].lex.length) == end_idx:
                end = i + 1
                break
        else:
            return None
        # Get LexemeC for newly merged token
        cdef UniStr new_orth_c
        slice_unicode(&new_orth_c, self._string, start_idx, end_idx)
        cdef const LexemeC* lex = self.vocab.get(self.mem, &new_orth_c)
        # House the new merged token where it starts
        cdef TokenC* token = &self.data[start]
        # Update fields
        token.lex = lex
        # What to do about morphology??
        # TODO: token.morph = ???
        token.tag = self.vocab.strings[tag]
        token.lemma = self.vocab.strings[lemma] 
        if ent_type == 'O':
            token.ent_iob = 2
            token.ent_type = 0
        else:
            token.ent_iob = 3
            token.ent_type = self.vocab.strings[ent_type]
        # Fix dependencies
        # Begin by setting all the head indices to absolute token positions
        # This is easier to work with for now than the offsets
        for i in range(self.length):
            self.data[i].head += i
        # Find the head of the merged token, and its dep relation
        outer_heads = {}
        for i in range(start, end):
            head_idx = self.data[i].head
            if head_idx == i or head_idx < start or head_idx >= end:
                # Don't consider "heads" which are actually dominated by a word
                # in the region we're merging
                gp = head_idx
                while self.data[gp].head != gp:
                    if start <= gp < end:
                        break
                    gp = self.data[gp].head
                else:
                    # If we have multiple words attaching to the same head,
                    # but with different dep labels, we're preferring the last
                    # occurring dep label. Shrug. What else could we do, I guess?
                    outer_heads[head_idx] = self.data[i].dep

        token.head, token.dep = max(outer_heads.items())
        # Adjust deps before shrinking tokens
        # Tokens which point into the merged token should now point to it
        # Subtract the offset from all tokens which point to >= end
        offset = (end - start) - 1
        for i in range(self.length):
            head_idx = self.data[i].head
            if start <= head_idx < end:
                self.data[i].head = start
            elif head_idx >= end:
                self.data[i].head -= offset
        # TODO: Fix left and right deps
        # Now compress the token array
        for i in range(end, self.length):
            self.data[i - offset] = self.data[i]
        for i in range(self.length - offset, self.length):
            memset(&self.data[i], 0, sizeof(TokenC))
            self.data[i].lex = &EMPTY_LEXEME
        self.length -= offset
        for i in range(self.length):
            # ...And, set heads back to a relative position
            self.data[i].head -= i

        # Clear cached Python objects
        self._py_tokens = [None] * self.length
        # Return the merged Python object
        return self[start]
 

cdef class Token:
    """An individual token --- i.e. a word, a punctuation symbol, etc.  Created
    via Tokens.__getitem__ and Tokens.__iter__.
    """
    def __cinit__(self, Vocab vocab, unicode string):
        self.vocab = vocab
        self._string = string

    def __dealloc__(self):
        if self._owns_c_data:
            # Cast through const, if we own the data
            PyMem_Free(<void*>self.c)

    def __len__(self):
        return self.c.lex.length

    def __unicode__(self):
        return self.string

    cpdef bint check_flag(self, attr_id_t flag_id) except -1:
        return check_flag(self.c.lex, flag_id)


    cdef int take_ownership_of_c_data(self) except -1:
        owned_data = <TokenC*>PyMem_Malloc(sizeof(TokenC) * self.array_len)
        memcpy(owned_data, self.c, sizeof(TokenC) * self.array_len)
        self.c = owned_data
        self._owns_c_data = True

    def nbor(self, int i=1):
        return Token.cinit(self.vocab, self._string,
                           self.c, self.i, self.array_len,
                           self._seq)

    property string:
        def __get__(self):
            cdef int next_idx = (self.c + 1).idx
            if next_idx < self.c.idx:
                next_idx = self.c.idx + self.c.lex.length
            return self._string[self.c.idx:next_idx]

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
            return numpy.asarray(<float[:300,]> self.c.lex.repvec)

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
            cdef const TokenC* ptr = self.c - self.i
            while ptr < self.c:
                # If this head is still to the right of us, we can skip to it
                # No token that's between this token and this head could be our
                # child.
                if (ptr.head >= 1) and (ptr + ptr.head) < self.c:
                    ptr += ptr.head

                elif ptr + ptr.head == self.c:
                    yield Token.cinit(self.vocab, self._string,
                                      ptr, ptr - (self.c - self.i), self.array_len,
                                      self._seq)
                    ptr += 1
                else:
                    ptr += 1

    property rights:
        def __get__(self):
            """The rightward immediate children of the word, in the syntactic
            dependency parse."""
            cdef const TokenC* ptr = (self.c - self.i) + (self.array_len - 1)
            tokens = []
            while ptr > self.c:
                # If this head is still to the right of us, we can skip to it
                # No token that's between this token and this head could be our
                # child.
                if (ptr.head < 0) and ((ptr + ptr.head) > self.c):
                    ptr += ptr.head
                elif ptr + ptr.head == self.c:
                    tokens.append(Token.cinit(self.vocab, self._string,
                                      ptr, ptr - (self.c - self.i), self.array_len,
                                      self._seq))
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

    property head:
        def __get__(self):
            """The token predicted by the parser to be the head of the current token."""
            return Token.cinit(self.vocab, self._string,
                               self.c + self.c.head, self.i + self.c.head, self.array_len,
                               self._seq)

    property ent_type_:
        def __get__(self):
            return self.vocab.strings[self.c.ent_type]

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


_pos_id_to_string = {id_: string for string, id_ in UNIV_POS_NAMES.items()}

_parse_unset_error = """Text has not been parsed, so cannot be accessed.

Check that the parser data is installed. Run "python -m spacy.en.download" if not.
Check whether parse=False in the call to English.__call__
"""

