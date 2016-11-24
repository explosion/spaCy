cimport cython
from libc.string cimport memcpy, memset
from libc.stdint cimport uint32_t
from libc.math cimport sqrt

import numpy
import numpy.linalg
import struct
cimport numpy as np
import six
import warnings

from ..lexeme cimport Lexeme
from ..lexeme cimport EMPTY_LEXEME
from ..typedefs cimport attr_t, flags_t
from ..attrs cimport attr_id_t
from ..attrs cimport ID, ORTH, NORM, LOWER, SHAPE, PREFIX, SUFFIX, LENGTH, CLUSTER
from ..attrs cimport POS, LEMMA, TAG, DEP, HEAD, SPACY, ENT_IOB, ENT_TYPE
from ..parts_of_speech cimport CONJ, PUNCT, NOUN
from ..parts_of_speech cimport univ_pos_t
from ..lexeme cimport Lexeme
from .span cimport Span
from .token cimport Token
from ..serialize.bits cimport BitArray
from ..util import normalize_slice
from ..syntax.iterators import CHUNKERS


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
        return Lexeme.get_struct_attr(token.lex, feat_name)


cdef class Doc:
    """
    A sequence of `Token` objects. Access sentences and named entities, 
    export annotations to numpy arrays, losslessly serialize to compressed 
    binary strings.

    Aside: Internals
        The `Doc` object holds an array of `TokenC` structs. 
        The Python-level `Token` and `Span` objects are views of this 
        array, i.e. they don't own the data themselves.

    Code: Construction 1
        doc = nlp.tokenizer(u'Some text')

    Code: Construction 2
        doc = Doc(nlp.vocab, orths_and_spaces=[(u'Some', True), (u'text', True)])

    """
    def __init__(self, Vocab vocab, words=None, spaces=None, orths_and_spaces=None):
        '''
        Create a Doc object.

        Aside: Implementation
            This method of constructing a `Doc` object is usually only used 
            for deserialization. Standard usage is to construct the document via 
            a call to the language object.

        Arguments:
            vocab:
                A Vocabulary object, which must match any models you want to 
                use (e.g. tokenizer, parser, entity recognizer).

            words:
                A list of unicode strings to add to the document as words. If None,
                defaults to empty list.

            spaces:
                A list of boolean values, of the same length as words. True
                means that the word is followed by a space, False means it is not.
                If None, defaults to [True]*len(words)
        '''
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
        self.user_hooks = {}
        self.user_token_hooks = {}
        self.user_span_hooks = {}
        self.tensor = numpy.zeros((0,), dtype='float32')
        self.user_data = {}
        self._py_tokens = []
        self._vector = None
        self.noun_chunks_iterator = CHUNKERS.get(self.vocab.lang)
        cdef unicode orth
        cdef bint has_space
        if orths_and_spaces is None and words is not None:
            if spaces is None:
                spaces = [True] * len(words)
            elif len(spaces) != len(words):
                raise ValueError(
                    "Arguments 'words' and 'spaces' should be sequences of the "
                    "same length, or 'spaces' should be left default at None. "
                    "spaces should be a sequence of booleans, with True meaning "
                    "that the word owns a ' ' character following it.")
            orths_and_spaces = zip(words, spaces)
        if orths_and_spaces is not None:
            for orth_space in orths_and_spaces:
                if isinstance(orth_space, unicode):
                    orth = orth_space
                    has_space = True
                elif isinstance(orth_space, bytes):
                    raise ValueError(
                        "orths_and_spaces expects either List(unicode) or "
                        "List((unicode, bool)). Got bytes instance: %s" % (str(orth_space)))
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
    
    def __getitem__(self, object i):
        '''
        doc[i]
            Get the Token object at position i, where i is an integer. 
            Negative indexing is supported, and follows the usual Python 
            semantics, i.e. doc[-2] is doc[len(doc) - 2].
        doc[start : end]]
            Get a `Span` object, starting at position `start`
            and ending at position `end`, where `start` and
            `end` are token indices. For instance,
            `doc[2:5]` produces a span consisting of 
            tokens 2, 3 and 4. Stepped slices (e.g. `doc[start : end : step]`) 
            are not supported, as `Span` objects must be contiguous (cannot have gaps).
            You can use negative indices and open-ended ranges, which have their
            normal Python semantics.
        '''
        if isinstance(i, slice):
            start, stop = normalize_slice(len(self), i.start, i.stop, i.step)
            return Span(self, start, stop, label=0)

        if i < 0:
            i = self.length + i
        bounds_check(i, self.length, PADDING)
        if self._py_tokens[i] is not None:
            return self._py_tokens[i]
        else:
            return Token.cinit(self.vocab, &self.c[i], i, self)

    def __iter__(self):
        '''
        for token in doc
            Iterate over `Token`  objects, from which the annotations can 
            be easily accessed. This is the main way of accessing Token 
            objects, which are the main way annotations are accessed from 
            Python. If faster-than-Python speeds are required, you can 
            instead access the annotations as a numpy array, or access the 
            underlying C data directly from Cython.
        '''
        cdef int i
        for i in range(self.length):
            if self._py_tokens[i] is not None:
                yield self._py_tokens[i]
            else:
                yield Token.cinit(self.vocab, &self.c[i], i, self)

    def __len__(self):
        '''
        len(doc)
            The number of tokens in the document.
        '''
        return self.length

    def __unicode__(self):
        return u''.join([t.text_with_ws for t in self])

    def __bytes__(self):
        return u''.join([t.text_with_ws for t in self]).encode('utf-8')

    def __str__(self):
        if six.PY3:
            return self.__unicode__()
        return self.__bytes__()

    def __repr__(self):
        return self.__str__()

    @property
    def doc(self):
        return self

    def similarity(self, other):
        '''Make a semantic similarity estimate. The default estimate is cosine
        similarity using an average of word vectors.

        Arguments:
            other (object): The object to compare with. By default, accepts Doc,
                Span, Token and Lexeme objects.

        Return:
            score (float): A scalar similarity score. Higher is more similar.
        '''
        if 'similarity' in self.user_hooks:
            return self.user_hooks['similarity'](self, other)
        if self.vector_norm == 0 or other.vector_norm == 0:
            return 0.0
        return numpy.dot(self.vector, other.vector) / (self.vector_norm * other.vector_norm)

    property has_vector:
        '''
        A boolean value indicating whether a word vector is associated with the object.
        '''
        def __get__(self):
            if 'has_vector' in self.user_hooks:
                return self.user_hooks['has_vector'](self)
 
            return any(token.has_vector for token in self)

    property vector:
        '''
        A real-valued meaning representation. Defaults to an average of the token vectors.
        
        Type: numpy.ndarray[ndim=1, dtype='float32']
        '''
        def __get__(self):
            if 'vector' in self.user_hooks:
                return self.user_hooks['vector'](self)
            if self._vector is None:
                if len(self):
                    self._vector = sum(t.vector for t in self) / len(self)
                else:
                    return numpy.zeros((self.vocab.vectors_length,), dtype='float32')
            return self._vector

        def __set__(self, value):
            self._vector = value

    property vector_norm:
        def __get__(self):
            if 'vector_norm' in self.user_hooks:
                return self.user_hooks['vector_norm'](self)
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
    def string(self):
        return self.text
    
    property text:
        '''A unicode representation of the document text.'''
        def __get__(self):
            return u''.join(t.text_with_ws for t in self)

    property text_with_ws:
        '''An alias of Doc.text, provided for duck-type compatibility with Span and Token.'''
        def __get__(self):
            return self.text

    property ents:
        '''
        Yields named-entity `Span` objects, if the entity recognizer
        has been applied to the document. Iterate over the span to get 
        individual Token objects, or access the label:

        Example:
            from spacy.en import English
            nlp = English()
            tokens = nlp(u'Mr. Best flew to New York on Saturday morning.')
            ents = list(tokens.ents)
            assert ents[0].label == 346
            assert ents[0].label_ == 'PERSON'
            assert ents[0].orth_ == 'Best'
            assert ents[0].text == 'Mr. Best'
        '''
        def __get__(self):
            cdef int i
            cdef const TokenC* token
            cdef int start = -1
            cdef int label = 0
            output = []
            for i in range(self.length):
                token = &self.c[i]
                if token.ent_iob == 1:
                    assert start != -1
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
            # 2. Ensure pre-set NERs are not over-written during statistical prediction
            # 3. Test basic data-driven ORTH gazetteer
            # 4. Test more nuanced date and currency regex
            cdef int i
            for i in range(self.length):
                self.c[i].ent_type = 0
                # At this point we don't know whether the NER has run over the 
                # Doc. If the ent_iob is missing, leave it missing.
                if self.c[i].ent_iob != 0:
                    self.c[i].ent_iob = 2 # Means O. Non-O are set from ents.
            cdef attr_t ent_type
            cdef int start, end
            for ent_info in ents:
                if isinstance(ent_info, Span):
                    ent_id = ent_info.ent_id
                    ent_type = ent_info.label
                    start = ent_info.start
                    end = ent_info.end
                elif len(ent_info) == 3:
                    ent_type, start, end = ent_info
                else:
                    ent_id, ent_type, start, end = ent_info
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

    property noun_chunks:
        '''
        Yields base noun-phrase #[code Span] objects, if the document
        has been syntactically parsed. A base noun phrase, or 
        'NP chunk', is a noun phrase that does not permit other NPs to 
        be nested within it – so no NP-level coordination, no prepositional 
        phrases, and no relative clauses. For example:
        '''
        def __get__(self):
            if not self.is_parsed:
                raise ValueError(
                    "noun_chunks requires the dependency parse, which "
                    "requires data to be installed. If you haven't done so, run: "
                    "\npython -m spacy.%s.download all\n"
                    "to install the data" % self.vocab.lang)
            # Accumulate the result before beginning to iterate over it. This prevents
            # the tokenisation from being changed out from under us during the iteration.
            # The tricky thing here is that Span accepts its tokenisation changing,
            # so it's okay once we have the Span objects. See Issue #375
            spans = []
            for start, end, label in self.noun_chunks_iterator(self):
                spans.append(Span(self, start, end, label=label))
            for span in spans:
                yield span

    property sents:
        """
        Yields sentence `Span` objects. Sentence spans have no label.
        To improve accuracy on informal texts, spaCy calculates sentence
        boundaries from the syntactic dependency parse. If the parser is disabled,
        `sents` iterator will be unavailable.

        Example:
            from spacy.en import English
            nlp = English()
            doc = nlp("This is a sentence. Here's another...")
            assert [s.root.orth_ for s in doc.sents] == ["is", "'s"]
        """
        def __get__(self):
            if 'sents' in self.user_hooks:
                return self.user_hooks['sents'](self)
 
            if not self.is_parsed:
                raise ValueError(
                    "sentence boundary detection requires the dependency parse, which "
                    "requires data to be installed. If you haven't done so, run: "
                    "\npython -m spacy.%s.download all\n"
                    "to install the data" % self.vocab.lang)
            cdef int i
            start = 0
            for i in range(1, self.length):
                if self.c[i].sent_start:
                    yield Span(self, start, i)
                    start = i
            if start != self.length:
                yield Span(self, start, self.length)

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
        assert t.lex.orth != 0
        t.spacy = has_space
        self.length += 1
        self._py_tokens.append(None)
        return t.idx + t.lex.length + t.spacy

    @cython.boundscheck(False)
    cpdef np.ndarray to_array(self, object py_attr_ids):
        """
        Given a list of M attribute IDs, export the tokens to a numpy 
        `ndarray` of shape (N, M), where `N` is the length 
        of the document. The values will be 32-bit integers.

        Example:
            from spacy import attrs
            doc = nlp(text)
            # All strings mapped to integers, for easy export to numpy
            np_array = doc.to_array([attrs.LOWER, attrs.POS, attrs.ENT_TYPE, attrs.IS_ALPHA])
                
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
                output[i, j] = get_token_attr(&self.c[i], feature)
        return output

    def count_by(self, attr_id_t attr_id, exclude=None, PreshCounter counts=None):
        """Produce a dict of {attribute (int): count (ints)} frequencies, keyed
        by the values of the given attribute ID.

        Example:
            from spacy.en import English, attrs
            nlp = English()
            tokens = nlp(u'apple apple orange banana')
            tokens.count_by(attrs.ORTH)
            # {12800L: 1, 11880L: 2, 7561L: 1}
            tokens.to_array([attrs.ORTH])
            # array([[11880],
            #   [11880],
            #   [ 7561],
            #   [12800]])

        Arguments:
            attr_id
                int
                The attribute ID to key the counts.
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
        '''Write to a `Doc` object, from an `(M, N)` array of attributes.
        '''
        cdef int i, col
        cdef attr_id_t attr_id
        cdef TokenC* tokens = self.c
        cdef int length = len(array)
        cdef attr_t[:] values
        for col, attr_id in enumerate(attrs): 
            values = array[:, col]
            if attr_id == HEAD:
                for i in range(length):
                    tokens[i].head = values[i]
                    if values[i] >= 1:
                        tokens[i + values[i]].l_kids += 1
                    elif values[i] < 0:
                        tokens[i + values[i]].r_kids += 1
            elif attr_id == TAG:
                for i in range(length):
                    if values[i] != 0:
                        self.vocab.morphology.assign_tag(&tokens[i], values[i])
            elif attr_id == POS:
                for i in range(length):
                    tokens[i].pos = <univ_pos_t>values[i]
            elif attr_id == DEP:
                for i in range(length):
                    tokens[i].dep = values[i]
            elif attr_id == ENT_IOB:
                for i in range(length):
                    tokens[i].ent_iob = values[i]
            elif attr_id == ENT_TYPE:
                for i in range(length):
                    tokens[i].ent_type = values[i]
            else:
                raise ValueError("Unknown attribute ID: %d" % attr_id)
        set_children_from_heads(self.c, self.length)
        self.is_parsed = bool(HEAD in attrs or DEP in attrs)
        self.is_tagged = bool(TAG in attrs or POS in attrs)
        return self

    def to_bytes(self):
        '''Serialize, producing a byte string.'''
        byte_string = self.vocab.serializer.pack(self)
        cdef uint32_t length = len(byte_string)
        return struct.pack('I', length) + byte_string

    def from_bytes(self, data):
        '''Deserialize, loading from bytes.'''
        self.vocab.serializer.unpack_into(data[4:], self)
        return self
    
    @staticmethod
    def read_bytes(file_):
        '''
        A static method, used to read serialized #[code Doc] objects from 
        a file. For example:

        Example:
            from spacy.tokens.doc import Doc
            loc = 'test_serialize.bin'
            with open(loc, 'wb') as file_:
                file_.write(nlp(u'This is a document.').to_bytes())
                file_.write(nlp(u'This is another.').to_bytes())
            docs = []
            with open(loc, 'rb') as file_:
                for byte_string in Doc.read_bytes(file_):
                    docs.append(Doc(nlp.vocab).from_bytes(byte_string))
            assert len(docs) == 2
        '''
        keep_reading = True
        while keep_reading:
            try:
                n_bytes_str = file_.read(4)
                if len(n_bytes_str) < 4:
                    break
                n_bytes = struct.unpack('I', n_bytes_str)[0]
                data = file_.read(n_bytes)
            except StopIteration:
                keep_reading = False
            yield n_bytes_str + data

    def merge(self, int start_idx, int end_idx, *args, **attributes):
        """Retokenize the document, such that the span at doc.text[start_idx : end_idx]
        is merged into a single token. If start_idx and end_idx do not mark start
        and end token boundaries, the document remains unchanged.

        Arguments:
            start_idx (int): The character index of the start of the slice to merge.
            end_idx (int): The character index after the end of the slice to merge.
            **attributes:
                Attributes to assign to the merged token. By default, attributes
                are inherited from the syntactic root token of the span.
        Returns:
            token (Token):
                The newly merged token, or None if the start and end indices did
                not fall at token boundaries.

        """
        cdef unicode tag, lemma, ent_type
        if len(args) == 3:
            # TODO: Warn deprecation
            tag, lemma, ent_type = args
            attributes[TAG] = self.vocab.strings[tag]
            attributes[LEMMA] = self.vocab.strings[lemma]
            attributes[ENT_TYPE] = self.vocab.strings[ent_type]
        elif args:
            raise ValueError(
                "Doc.merge received %d non-keyword arguments. "
                "Expected either 3 arguments (deprecated), or 0 (use keyword arguments). "
                "Arguments supplied:\n%s\n"
                "Keyword arguments:%s\n" % (len(args), repr(args), repr(attributes)))
 
        cdef int start = token_by_start(self.c, self.length, start_idx)
        if start == -1:
            return None
        cdef int end = token_by_end(self.c, self.length, end_idx)
        if end == -1:
            return None
        # Currently we have the token index, we want the range-end index
        end += 1
        cdef Span span = self[start:end]
        tag = self.vocab.strings[attributes.get(TAG, span.root.tag)]
        lemma = self.vocab.strings[attributes.get(LEMMA, span.root.lemma)]
        ent_type = self.vocab.strings[attributes.get(ENT_TYPE, span.root.ent_type)]

        # Get LexemeC for newly merged token
        new_orth = ''.join([t.text_with_ws for t in span])
        if span[-1].whitespace_:
            new_orth = new_orth[:-len(span[-1].whitespace_)]
        cdef const LexemeC* lex = self.vocab.get(self.mem, new_orth)
        # House the new merged token where it starts
        cdef TokenC* token = &self.c[start]
        token.spacy = self.c[end-1].spacy
        if tag in self.vocab.morphology.tag_map:
            self.vocab.morphology.assign_tag(token, tag)
        else:
            token.tag = self.vocab.strings[tag]
        token.lemma = self.vocab.strings[lemma]
        if ent_type == 'O':
            token.ent_iob = 2
            token.ent_type = 0
        else:
            token.ent_iob = 3
            token.ent_type = self.vocab.strings[ent_type]
        # Begin by setting all the head indices to absolute token positions
        # This is easier to work with for now than the offsets
        # Before thinking of something simpler, beware the case where a dependency
        # bridges over the entity. Here the alignment of the tokens changes.
        span_root = span.root.i
        token.dep = span.root.dep
        # We update token.lex after keeping span root and dep, since
        # setting token.lex will change span.start and span.end properties
        # as it modifies the character offsets in the doc
        token.lex = lex
        for i in range(self.length):
            self.c[i].head += i
        # Set the head of the merged token, and its dep relation, from the Span
        token.head = self.c[span_root].head
        # Adjust deps before shrinking tokens
        # Tokens which point into the merged token should now point to it
        # Subtract the offset from all tokens which point to >= end
        offset = (end - start) - 1
        for i in range(self.length):
            head_idx = self.c[i].head
            if start <= head_idx < end:
                self.c[i].head = start
            elif head_idx >= end:
                self.c[i].head -= offset
        # Now compress the token array
        for i in range(end, self.length):
            self.c[i - offset] = self.c[i]
        for i in range(self.length - offset, self.length):
            memset(&self.c[i], 0, sizeof(TokenC))
            self.c[i].lex = &EMPTY_LEXEME
        self.length -= offset
        for i in range(self.length):
            # ...And, set heads back to a relative position
            self.c[i].head -= i
        # Set the left/right children, left/right edges
        set_children_from_heads(self.c, self.length)
        # Clear the cached Python objects
        self._py_tokens = [None] * self.length
        # Return the merged Python object
        return self[start]


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
    # Set left edges
    for i in range(length):
        child = &tokens[i]
        head = &tokens[i + child.head]
        if child < head:
            if child.l_edge < head.l_edge:
                head.l_edge = child.l_edge
            head.l_kids += 1
        
    # Set right edges --- same as above, but iterate in reverse
    for i in range(length-1, -1, -1):
        child = &tokens[i]
        head = &tokens[i + child.head]
        if child > head:
            if child.r_edge > head.r_edge:
                head.r_edge = child.r_edge
            head.r_kids += 1

    # Set sentence starts
    for i in range(length):
        if tokens[i].head == 0 and tokens[i].dep != 0:
            tokens[tokens[i].l_edge].sent_start = True
            
