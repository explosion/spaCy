# cython: embedsignature=True
# coding: utf8
from __future__ import unicode_literals, print_function

from libc.math cimport sqrt
from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64

# Compiler crashes on memory view coercion without this. Should report bug.
from cython.view cimport array as cvarray
cimport numpy as np
np.import_array()

from libc.string cimport memset
import numpy

from .typedefs cimport attr_t, flags_t
from .attrs cimport IS_ALPHA, IS_ASCII, IS_DIGIT, IS_LOWER, IS_PUNCT, IS_SPACE
from .attrs cimport IS_TITLE, IS_UPPER, LIKE_URL, LIKE_NUM, LIKE_EMAIL, IS_STOP
from .attrs cimport IS_BRACKET
from .attrs cimport IS_QUOTE
from .attrs cimport IS_LEFT_PUNCT
from .attrs cimport IS_RIGHT_PUNCT
from .attrs cimport IS_OOV
from . import about


memset(&EMPTY_LEXEME, 0, sizeof(LexemeC))


cdef class Lexeme:
    """An entry in the vocabulary. A `Lexeme` has no string context – it's a
    word-type, as opposed to a word token.  It therefore has no part-of-speech
    tag, dependency parse, or lemma (lemmatization depends on the part-of-speech
    tag).
    """
    def __init__(self, Vocab vocab, attr_t orth):
        """Create a Lexeme object.

        vocab (Vocab): The parent vocabulary
        orth (uint64): The orth id of the lexeme.
        Returns (Lexeme): The newly constructd object.
        """
        self.vocab = vocab
        self.orth = orth
        self.c = <LexemeC*><void*>vocab.get_by_orth(vocab.mem, orth)
        assert self.c.orth == orth

    def __richcmp__(self, other, int op):
        if isinstance(other, Lexeme):
            a = self.orth
            b = other.orth
        elif isinstance(other, long):
            a = self.orth
            b = other
        elif isinstance(other, str):
            a = self.orth_
            b = other
        else:
            a = 0
            b = 1
        if op == 2: # ==
            return a == b
        elif op == 3: # !=
            return a != b
        elif op == 0: # <
            return a < b
        elif op == 1: # <=
            return a <= b
        elif op == 4: # >
            return a > b
        elif op == 5: # >=
            return a >= b
        else:
            raise NotImplementedError(op)

    def __hash__(self):
        return self.c.orth

    def set_flag(self, attr_id_t flag_id, bint value):
        """Change the value of a boolean flag.

        flag_id (int): The attribute ID of the flag to set.
        value (bool): The new value of the flag.
        """
        Lexeme.c_set_flag(self.c, flag_id, value)

    def check_flag(self, attr_id_t flag_id):
        """Check the value of a boolean flag.

        flag_id (int): The attribute ID of the flag to query.
        RETURNS (bool): The value of the flag.
        """
        return True if Lexeme.c_check_flag(self.c, flag_id) else False

    def similarity(self, other):
        """Compute a semantic similarity estimate. Defaults to cosine over
        vectors.

        other (object): The object to compare with. By default, accepts `Doc`,
            `Span`, `Token` and `Lexeme` objects.
        RETURNS (float): A scalar similarity score. Higher is more similar.
        """
        if self.vector_norm == 0 or other.vector_norm == 0:
            return 0.0
        return numpy.dot(self.vector, other.vector) / (self.vector_norm * other.vector_norm)

    def to_bytes(self):
        lex_data = Lexeme.c_to_bytes(self.c)
        start = <const char*>&self.c.flags
        end = <const char*>&self.c.sentiment + sizeof(self.c.sentiment)
        assert (end-start) == sizeof(lex_data.data), (end-start, sizeof(lex_data.data))
        byte_string = b'\0' * sizeof(lex_data.data)
        byte_chars = <char*>byte_string
        for i in range(sizeof(lex_data.data)):
            byte_chars[i] = lex_data.data[i]
        assert len(byte_string) == sizeof(lex_data.data), (len(byte_string),
                sizeof(lex_data.data))
        return byte_string

    def from_bytes(self, bytes byte_string):
        # This method doesn't really have a use-case --- wrote it for testing.
        # Possibly delete? It puts the Lexeme out of synch with the vocab.
        cdef SerializedLexemeC lex_data
        assert len(byte_string) == sizeof(lex_data.data)
        for i in range(len(byte_string)):
            lex_data.data[i] = byte_string[i]
        Lexeme.c_from_bytes(self.c, lex_data)
        self.orth = self.c.orth

    property has_vector:
        """A boolean value indicating whether a word vector is associated with
        the object.

        RETURNS (bool): Whether a word vector is associated with the object.
        """
        def __get__(self):
            return self.vocab.has_vector(self.c.orth)

    property vector_norm:
        """The L2 norm of the lexeme's vector representation.

        RETURNS (float): The L2 norm of the vector representation.
        """
        def __get__(self):
            vector = self.vector
            return numpy.sqrt((vector**2).sum())

    property vector:
        """A real-valued meaning representation.

        RETURNS (numpy.ndarray[ndim=1, dtype='float32']): A 1D numpy array
            representing the lexeme's semantics.
        """
        def __get__(self):
            cdef int length = self.vocab.vectors_length
            if length == 0:
                raise ValueError(
                    "Word vectors set to length 0. This may be because you "
                    "don't have a model installed or loaded, or because your "
                    "model doesn't include word vectors. For more info, see "
                    "the documentation: \n%s\n" % about.__docs_models__
                )
            return self.vocab.get_vector(self.c.orth)

        def __set__(self, vector):
            assert len(vector) == self.vocab.vectors_length
            self.vocab.set_vector(self.c.orth, vector)

    property rank:
        def __get__(self):
            return self.c.id
        def __set__(self, value):
            self.c.id = value

    property sentiment:
        def __get__(self):
            return self.c.sentiment
        def __set__(self, float sentiment):
            self.c.sentiment = sentiment

    property orth_:
        def __get__(self):
            return self.vocab.strings[self.c.orth]

    property text:
        """A unicode representation of the token text.

        RETURNS (unicode): The original verbatim text of the token.
        """
        def __get__(self):
            return self.orth_

    property lower:
        def __get__(self): return self.c.lower
        def __set__(self, attr_t x): self.c.lower = x

    property norm:
        def __get__(self): return self.c.norm
        def __set__(self, attr_t x): self.c.norm = x

    property shape:
        def __get__(self): return self.c.shape
        def __set__(self, attr_t x): self.c.shape = x

    property prefix:
        def __get__(self): return self.c.prefix
        def __set__(self, attr_t x): self.c.prefix = x

    property suffix:
        def __get__(self): return self.c.suffix
        def __set__(self, attr_t x): self.c.suffix = x

    property cluster:
        def __get__(self): return self.c.cluster
        def __set__(self, attr_t x): self.c.cluster = x

    property lang:
        def __get__(self): return self.c.lang
        def __set__(self, attr_t x): self.c.lang = x

    property prob:
        def __get__(self): return self.c.prob
        def __set__(self, float x): self.c.prob = x

    property lower_:
        def __get__(self): return self.vocab.strings[self.c.lower]
        def __set__(self, unicode x): self.c.lower = self.vocab.strings.add(x)

    property norm_:
        def __get__(self): return self.vocab.strings[self.c.norm]
        def __set__(self, unicode x): self.c.norm = self.vocab.strings.add(x)

    property shape_:
        def __get__(self): return self.vocab.strings[self.c.shape]
        def __set__(self, unicode x): self.c.shape = self.vocab.strings.add(x)

    property prefix_:
        def __get__(self): return self.vocab.strings[self.c.prefix]
        def __set__(self, unicode x): self.c.prefix = self.vocab.strings.add(x)

    property suffix_:
        def __get__(self): return self.vocab.strings[self.c.suffix]
        def __set__(self, unicode x): self.c.suffix = self.vocab.strings.add(x)

    property lang_:
        def __get__(self): return self.vocab.strings[self.c.lang]
        def __set__(self, unicode x): self.c.lang = self.vocab.strings.add(x)

    property flags:
        def __get__(self): return self.c.flags
        def __set__(self, flags_t x): self.c.flags = x

    property is_oov:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_OOV)
        def __set__(self, attr_t x): Lexeme.c_set_flag(self.c, IS_OOV, x)

    property is_stop:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_STOP)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_STOP, x)

    property is_alpha:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_ALPHA)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_ALPHA, x)

    property is_ascii:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_ASCII)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_ASCII, x)

    property is_digit:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_DIGIT)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_DIGIT, x)

    property is_lower:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_LOWER)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_LOWER, x)

    property is_title:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_TITLE)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_TITLE, x)

    property is_punct:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_PUNCT)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_PUNCT, x)

    property is_space:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_SPACE)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_SPACE, x)

    property is_bracket:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_BRACKET)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_BRACKET, x)

    property is_quote:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_QUOTE)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_QUOTE, x)

    property is_left_punct:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_LEFT_PUNCT)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_LEFT_PUNCT, x)

    property is_right_punct:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_RIGHT_PUNCT)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_RIGHT_PUNCT, x)

    property like_url:
        def __get__(self): return Lexeme.c_check_flag(self.c, LIKE_URL)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, LIKE_URL, x)

    property like_num:
        def __get__(self): return Lexeme.c_check_flag(self.c, LIKE_NUM)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, LIKE_NUM, x)

    property like_email:
        def __get__(self): return Lexeme.c_check_flag(self.c, LIKE_EMAIL)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, LIKE_EMAIL, x)
