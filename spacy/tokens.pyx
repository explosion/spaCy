# cython: embedsignature=True
from cython.view cimport array as cvarray

from preshed.maps cimport PreshMap
from preshed.counter cimport PreshCounter

from .vocab cimport EMPTY_LEXEME
from .typedefs cimport attr_id_t, attr_t
from .typedefs cimport LEMMA
from .typedefs cimport ID, ORTH, NORM, LOWER, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER
from .typedefs cimport POS, LEMMA

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
    """Access and set annotations onto some text.
    """
    def __init__(self, Vocab vocab, unicode string):
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

    def sentences(self):
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

    def __getitem__(self, i):
        """Retrieve a token.
        
        Returns:
            token (Token):
        """
        if i < 0:
            i = self.length - i
        bounds_check(i, self.length, PADDING)
        return Token(self, i)

    def __iter__(self):
        """Iterate over the tokens.

        Yields:
            token (Token):
        """
        for i in range(self.length):
            yield self[i]

    def __len__(self):
        return self.length

    def __unicode__(self):
        cdef const TokenC* last = &self.data[self.length - 1]
        return self._string[:last.idx + last.lex.length]

    def __str__(self):
        return unidecode(unicode(self))

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
        return idx + t.lex.length

    @cython.boundscheck(False)
    cpdef long[:,:] to_array(self, object attr_ids):
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
        cdef long[:,:] output = cvarray(shape=(self.length, len(attr_ids)),
                                        itemsize=sizeof(long), format="l")
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


@cython.freelist(64)
cdef class Token:
    """An individual token."""
    def __init__(self, Tokens tokens, int i):
        self._seq = tokens
        self.i = i
        cdef const TokenC* t = &tokens.data[i]
        self.idx = t.idx
        self.cluster = t.lex.cluster
        self.length = t.lex.length
        self.orth = t.lex.orth
        self.lower = t.lex.lower
        self.norm = t.lex.norm
        self.shape = t.lex.shape
        self.prefix = t.lex.prefix
        self.suffix = t.lex.suffix
        self.prob = t.lex.prob
        self.sentiment = t.lex.sentiment
        self.flags = t.lex.flags
        self.lemma = t.lemma
        self.tag = t.tag
        self.dep = t.dep
        self.repvec = numpy.asarray(<float[:300,]> t.lex.repvec)
        cdef int next_idx = (t+1).idx
        if next_idx <= self.idx:
            next_idx = self.idx + self.length
        self.string = tokens._string[self.idx:next_idx]

    def __len__(self):
        """The number of unicode code-points in the original string.

        Returns:
            length (int):
        """
        return self._seq.data[self.i].lex.length

    property head:
        """The token predicted by the parser to be the head of the current token."""
        def __get__(self):
            cdef const TokenC* t = &self._seq.data[self.i]
            return Token(self._seq, self.i + t.head)

    property whitespace:
        def __get__(self):
            return self.string[self.length:]

    property orth_:
        def __get__(self):
            return self._seq.vocab.strings[self.orth]

    property lower_:
        def __get__(self):
            return self._seq.vocab.strings[self.lower]

    property norm_:
        def __get__(self):
            return self._seq.vocab.strings[self.norm]

    property shape_:
        def __get__(self):
            return self._seq.vocab.strings[self.shape]

    property prefix_:
        def __get__(self):
            return self._seq.vocab.strings[self.prefix]

    property suffix_:
        def __get__(self):
            return self._seq.vocab.strings[self.suffix]

    property lemma_:
        def __get__(self):
            cdef const TokenC* t = &self._seq.data[self.i]
            if t.lemma == 0:
                return self.string
            cdef unicode py_ustr = self._seq.vocab.strings[t.lemma]
            return py_ustr

    property tag_:
        def __get__(self):
            return self._seq.tag_names[self.tag]

    property dep_:
        def __get__(self):
            return self._seq.dep_names[self.dep]
