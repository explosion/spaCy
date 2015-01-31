# cython: embedsignature=True

from preshed.maps cimport PreshMap
from preshed.counter cimport PreshCounter

from .vocab cimport EMPTY_LEXEME
from .typedefs cimport attr_id_t, attr_t
from .typedefs cimport LEMMA
from .typedefs cimport ID, ORTH, NORM, LOWER, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER
from .typedefs cimport POS, LEMMA
from .parts_of_speech import UNIV_POS_NAMES

from unidecode import unidecode

cimport numpy
import numpy

cimport cython


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
        self._tag_strings = tuple() # These will be set by the POS tagger and parser
        self._dep_strings = tuple() # The strings are arbitrary and model-specific.

    def __getitem__(self, object i):
        """Retrieve a token.
        
        The Python Token objects are created lazily from internal C data, and
        cached in _py_tokens
        
        Returns:
            token (Token):
        """
        if i < 0:
            i = self.length - i
        bounds_check(i, self.length, PADDING)
        return Token.cinit(self.mem, self.vocab, self._string,
                           &self.data[i], i, self.length,
                           self._py_tokens, self._tag_strings, self._dep_strings)

    def __iter__(self):
        """Iterate over the tokens.

        Yields:
            token (Token):
        """
        for i in range(self.length):
            yield Token.cinit(self.mem, self.vocab, self._string,
                              &self.data[i], i, self.length,
                              self._py_tokens, self._tag_strings, self._dep_strings)

    def __len__(self):
        return self.length

    def __unicode__(self):
        cdef const TokenC* last = &self.data[self.length - 1]
        return self._string[:last.idx + last.lex.length]

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
        sentences = []
        cdef Tokens sent = Tokens(self.vocab, self._string[self.data[0].idx:])
        cdef attr_t period = self.vocab.strings['.']
        cdef attr_t question = self.vocab.strings['?']
        cdef attr_t exclamation = self.vocab.strings['!']
        spans = []
        start = None
        for i in range(self.length):
            if start is None:
                start = i
            if self.data[i].lex.orth == period or self.data[i].lex.orth == exclamation or \
              self.data[i].lex.orth == question:
                spans.append((start, i+1))
                start = None
        if start is not None:
            spans.append((start, self.length))
        return spans


cdef class Token:
    """An individual token."""
    def __cinit__(self, Pool mem, Vocab vocab, unicode string):
        self.mem = mem
        self.vocab = vocab
        self._string = string

    def __len__(self):
        return self.c.lex.length

    def nbor(self, int i=1):
        return Token.cinit(self.mem, self.vocab, self._string,
                           self.c, self.i, self.array_len,
                           self._py, self._tag_strings, self._dep_strings)

    @property
    def string(self):
        cdef int next_idx = (self.c + 1).idx
        if next_idx < self.c.idx:
            next_idx = self.c.idx + self.c.lex.length
        return self._string[self.c.idx:next_idx]

    @property
    def idx(self):
        return self.c.idx

    @property
    def cluster(self):
        return self.c.lex.cluster

    @property
    def cluster(self):
        return self.c.lex.cluster

    @property
    def orth(self):
        return self.c.lex.orth

    @property
    def lower(self):
        return self.c.lex.lower

    @property
    def norm(self):
        return self.c.lex.norm

    @property
    def shape(self):
        return self.c.lex.shape

    @property
    def prefix(self):
        return self.c.lex.prefix

    @property
    def suffix(self):
        return self.c.lex.suffix

    @property
    def lemma(self):
        return self.c.lemma

    @property
    def pos(self):
        return self.c.pos

    @property
    def tag(self):
        return self.c.tag

    @property
    def dep(self):
        return self.c.dep

    @property
    def repvec(self):
        return numpy.asarray(<float[:300,]> self.c.lex.repvec)

    @property 
    def n_lefts(self):
        cdef int n = 0
        cdef const TokenC* ptr = self.c - self.i
        while ptr != self.c:
            if ptr + ptr.head == self.c:
                n += 1
            ptr += 1
        return n

    @property 
    def n_rights(self):
        cdef int n = 0
        cdef const TokenC* ptr = self.c + (self.array_len - self.i)
        while ptr != self.c:
            if ptr + ptr.head == self.c:
                n += 1
            ptr -= 1
        return n

    @property 
    def lefts(self):
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
                yield Token.cinit(self.mem, self.vocab, self._string,
                                  ptr, self.i, self.array_len,
                                  self._py, self._tag_strings, self._dep_strings)
                ptr += 1
            else:
                ptr += 1

    @property
    def rights(self):
        """The rightward immediate children of the word, in the syntactic
        dependency parse."""
        cdef const TokenC* ptr = (self.c - self.i) + (self.array_len - 1)
        while ptr > self.c:
            # If this head is still to the right of us, we can skip to it
            # No token that's between this token and this head could be our
            # child.
            if (ptr.head < 0) and ((ptr + ptr.head) > self.c):
                ptr += ptr.head
            elif ptr + ptr.head == self.c:
                yield Token.cinit(self.mem, self.vocab, self._string,
                                  ptr, self.i, self.array_len,
                                  self._py, self._tag_strings, self._dep_strings)
                ptr -= 1
            else:
                ptr -= 1

    @property
    def head(self):
        """The token predicted by the parser to be the head of the current token."""
        return Token.cinit(self.mem, self.vocab, self._string,
                           self.c + self.c.head, self.i, self.array_len,
                           self._py, self._tag_strings, self._dep_strings)

    @property
    def whitespace_(self):
        return self.string[self.c.lex.length:]

    @property
    def orth_(self):
        return self.vocab.strings[self.c.lex.orth]

    @property
    def lower_(self):
        return self.vocab.strings[self.c.lex.lower]

    @property
    def norm_(self):
        return self.vocab.strings[self.c.lex.norm]

    @property
    def shape_(self):
        return self.vocab.strings[self.c.lex.shape]

    @property
    def prefix_(self):
        return self.vocab.strings[self.c.lex.prefix]

    @property
    def suffix_(self):
        return self.vocab.strings[self.c.lex.suffix]

    @property
    def lemma_(self):
        return self.vocab.strings[self.c.lemma]

    @property
    def pos_(self):
        return _pos_id_to_string[self.c.pos]

    @property
    def tag_(self):
        return self._tag_strings[self.c.tag]

    @property
    def dep_(self):
        return self._dep_strings[self.c.dep]


_pos_id_to_string = {id_: string for string, id_ in UNIV_POS_NAMES.items()}

_parse_unset_error = """Text has not been parsed, so cannot be accessed.

Check that the parser data is installed. Run "python -m spacy.en.download" if not.
Check whether parse=False in the call to English.__call__
"""

