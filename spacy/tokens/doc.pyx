cimport cython
from libc.string cimport memcpy, memset

import numpy

from ..lexeme cimport EMPTY_LEXEME
from ..strings cimport slice_unicode
from ..typedefs cimport attr_t, flags_t
from ..attrs cimport attr_id_t
from ..attrs cimport ID, ORTH, NORM, LOWER, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER
from ..attrs cimport POS, LEMMA, TAG, DEP, HEAD, SPACY, ENT_IOB, ENT_TYPE
from ..parts_of_speech import UNIV_POS_NAMES
from ..parts_of_speech cimport CONJ, PUNCT
from ..lexeme cimport check_flag
from ..lexeme cimport get_attr as get_lex_attr
from .spans import Span
from ..structs cimport UniStr
from .token cimport Token


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
    elif feat_name == TAG:
        return token.tag
    elif feat_name == DEP:
        return token.dep
    elif feat_name == HEAD:
        return token.head
    elif feat_name == SPACY:
        return token.spacy
    elif feat_name == ENT_IOB:
        return token.ent_iob
    elif feat_name == ENT_TYPE:
        return token.ent_type
    else:
        return get_lex_attr(token.lex, feat_name)


cdef class Doc:
    """
    Container class for annotated text.  Constructed via English.__call__ or
    Tokenizer.__call__.
    """
    def __init__(self, Vocab vocab):
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
        self.data = data_start + PADDING
        self.max_length = size
        self.length = 0
        self.is_tagged = False
        self.is_parsed = False
        self._py_tokens = []

    @classmethod
    def from_ids(cls, Vocab vocab, orths, spaces):
        cdef int i
        cdef const LexemeC* lex
        cdef Doc self = cls(vocab)
        cdef bint space = 0
        cdef attr_t orth
        for i in range(len(orths)):
            orth = orths[i]
            lex = <LexemeC*>self.vocab._by_orth.get(orth)
            if lex != NULL:
                assert lex.orth == orth
                space = spaces[i]
                self.push_back(lex, space)
            else:
                raise Exception('Lexeme not found: %d' % orth)
        return self

    def __getitem__(self, object i):
        """Get a token.

        Returns:
            token (Token):
        """
        if isinstance(i, slice):
            if i.step is not None:
                raise ValueError("Stepped slices not supported in Span objects."
                                 "Try: list(doc)[start:stop:step] instead.")
            return Span(self, i.start, i.stop, label=0)

        if i < 0:
            i = self.length + i
        bounds_check(i, self.length, PADDING)
        if self._py_tokens[i] is not None:
            return self._py_tokens[i]
        else:
            return Token.cinit(self.vocab, &self.data[i], i, self)

    def __iter__(self):
        """Iterate over the tokens.

        Yields:
            token (Token):
        """
        cdef int i
        for i in range(self.length):
            if self._py_tokens[i] is not None:
                yield self._py_tokens[i]
            else:
                yield Token.cinit(self.vocab, &self.data[i], i, self)

    def __len__(self):
        return self.length

    def __unicode__(self):
        return u''.join([t.string for t in self])

    @property
    def string(self):
        return unicode(self)

    @property
    def ents(self):
        """Yields named-entity Span objects.
        
        Iterate over the span to get individual Token objects, or access the label:

        >>> from spacy.en import English
        >>> nlp = English()
        >>> tokens = nlp(u'Mr. Best flew to New York on Saturday morning.')
        >>> ents = list(tokens.ents)
        >>> ents[0].label, ents[0].label_, ''.join(t.orth_ for t in ents[0])
        (112504, u'PERSON', u'Best ') 
        """
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
                if start != -1:
                    yield Span(self, start, i, label=label)
                start = i
                label = token.ent_type
        if start != -1:
            yield Span(self, start, self.length, label=label)

    @property
    def sents(self):
        """
        Yield a list of sentence Span objects, calculated from the dependency parse.
        """
        cdef int i
        start = 0
        for i in range(1, self.length):
            if self.data[i].sent_start:
                yield Span(self, start, i)
                start = i
        yield Span(self, start, self.length)

    cdef int push_back(self, LexemeOrToken lex_or_tok, bint has_space) except -1:
        if self.length == self.max_length:
            self._realloc(self.length * 2)
        cdef TokenC* t = &self.data[self.length]
        if LexemeOrToken is TokenC_ptr:
            t[0] = lex_or_tok[0]
        else:
            t.lex = lex_or_tok
        if self.length == 0:
            t.idx = 0
        else:
            t.idx = (t-1).idx + (t-1).lex.length + (t-1).spacy
        t.spacy = has_space
        self.length += 1
        self._py_tokens.append(None)
        return t.idx + t.lex.length + t.spacy

    @cython.boundscheck(False)
    cpdef np.ndarray to_array(self, object py_attr_ids):
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
        cdef np.ndarray[attr_t, ndim=2] output
        # Make an array from the attributes --- otherwise our inner loop is Python
        # dict iteration.
        cdef np.ndarray[attr_t, ndim=1] attr_ids = numpy.asarray(py_attr_ids, dtype=numpy.int32)
        output = numpy.ndarray(shape=(self.length, len(attr_ids)), dtype=numpy.int32)
        for i in range(self.length):
            for j, feature in enumerate(attr_ids):
                output[i, j] = get_token_attr(&self.data[i], feature)
        return output

    def count_by(self, attr_id_t attr_id, exclude=None, PreshCounter counts=None):
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
        
        if counts is None:
            counts = PreshCounter(self.length)
            output_dict = True
        else:
            output_dict = False
        # Take this check out of the loop, for a bit of extra speed
        if exclude is None:
            for i in range(self.length):
                attr = get_token_attr(&self.data[i], attr_id)
                counts.inc(attr, 1)
        else:
            for i in range(self.length):
                if not exclude(self[i]):
                    attr = get_token_attr(&self.data[i], attr_id)
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
        cdef TokenC* data_start = self.data - PADDING
        data_start = <TokenC*>self.mem.realloc(data_start, n * sizeof(TokenC))
        self.data = data_start + PADDING
        cdef int i
        for i in range(self.length, self.max_length + PADDING):
            self.data[i].lex = &EMPTY_LEXEME

    cdef int set_parse(self, const TokenC* parsed) except -1:
        # TODO: This method is fairly misleading atm. It's used by Parser
        # to actually apply the parse calculated. Need to rethink this.
        self.is_parsed = True
        for i in range(self.length):
            self.data[i] = parsed[i]

    def merge(self, int start_idx, int end_idx, unicode tag, unicode lemma,
              unicode ent_type):
        """Merge a multi-word expression into a single token.  Currently
        experimental; API is likely to change."""
        cdef int i
        cdef int start = -1
        cdef int end = -1
        for i in range(self.length):
            if self.data[i].idx == start_idx:
                start = i
            if (self.data[i].idx + self.data[i].lex.length) == end_idx:
                if start == -1:
                    return None
                end = i + 1
                break
        else:
            return None
        cdef unicode string = self.string
        # Get LexemeC for newly merged token
        cdef UniStr new_orth_c
        slice_unicode(&new_orth_c, string, start_idx, end_idx)
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

        # Return the merged Python object
        return self[start]

    def from_array(self, attrs, array):
        cdef int i, col
        cdef attr_id_t attr_id
        cdef TokenC* tokens = self.data
        cdef int length = len(array)
        for col, attr_id in enumerate(attrs): 
            values = array[:, col]
            if attr_id == HEAD:
                for i in range(length):
                    tokens[i].head = values[i]
            elif attr_id == TAG:
                for i in range(length):
                    tokens[i].tag = values[i]
            elif attr_id == DEP:
                for i in range(length):
                    tokens[i].dep = values[i]
            elif attr_id == ENT_IOB:
                for i in range(length):
                    tokens[i].ent_iob = values[i]
            elif attr_id == ENT_TYPE:
                for i in range(length):
                    tokens[i].ent_type = values[i]
