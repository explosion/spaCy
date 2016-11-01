# cython: embedsignature=True
from libc.math cimport sqrt
from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64

# Compiler crashes on memory view coercion without this. Should report bug.
from cython.view cimport array as cvarray
cimport numpy as np
np.import_array()



from libc.string cimport memset

from .orth cimport word_shape
from .typedefs cimport attr_t, flags_t
import numpy

from .attrs cimport IS_ALPHA, IS_ASCII, IS_DIGIT, IS_LOWER, IS_PUNCT, IS_SPACE
from .attrs cimport IS_TITLE, IS_UPPER, LIKE_URL, LIKE_NUM, LIKE_EMAIL, IS_STOP
from .attrs cimport IS_BRACKET
from .attrs cimport IS_QUOTE
from .attrs cimport IS_LEFT_PUNCT
from .attrs cimport IS_RIGHT_PUNCT
from .attrs cimport IS_OOV


memset(&EMPTY_LEXEME, 0, sizeof(LexemeC))


cdef class Lexeme:
    """An entry in the vocabulary.  A Lexeme has no string context --- it's a
    word-type, as opposed to a word token.  It therefore has no part-of-speech
    tag, dependency parse, or lemma (lemmatization depends on the part-of-speech
    tag).
    """
    def __init__(self, Vocab vocab, int orth):
        """Create a Lexeme object.

        Arguments:
            vocab (Vocab): The parent vocabulary
            orth (int): The orth id of the lexeme.
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
        elif isinstance(other, int):
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

        Arguments:
            flag_id (int): The attribute ID of the flag to set.
            value (bool): The new value of the flag.
        """
        Lexeme.c_set_flag(self.c, flag_id, value)
    
    def check_flag(self, attr_id_t flag_id):
        """Check the value of a boolean flag.

        Arguments:
            flag_id (int): The attribute ID of the flag to query.
        Returns (bool): The value of the flag.
        """
        return True if Lexeme.c_check_flag(self.c, flag_id) else False

    def similarity(self, other):
        '''Compute a semantic similarity estimate. Defaults to cosine over vectors.

        Arguments:
            other:
                The object to compare with. By default, accepts Doc, Span,
                Token and Lexeme objects.
        Returns:
            score (float): A scalar similarity score. Higher is more similar.
        '''
        if self.vector_norm == 0 or other.vector_norm == 0:
            return 0.0
        return numpy.dot(self.vector, other.vector) / (self.vector_norm * other.vector_norm)

    property has_vector:
        def __get__(self):
            cdef int i
            for i in range(self.vocab.vectors_length):
                if self.c.vector[i] != 0:
                    return True
            else:
                return False

    property vector_norm:
        def __get__(self):
            return self.c.l2_norm

        def __set__(self, float value):
            self.c.l2_norm = value

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
 
            vector_view = <float[:length,]>self.c.vector
            return numpy.asarray(vector_view)

        def __set__(self, vector):
            assert len(vector) == self.vocab.vectors_length
            cdef float value
            cdef double norm = 0.0
            for i, value in enumerate(vector):
                self.c.vector[i] = value
                norm += value * value
            self.c.l2_norm = sqrt(norm)

    property rank:
        def __get__(self):
            return self.c.id

    property repvec:
        def __get__(self):
            raise AttributeError("lex.repvec has been renamed to lex.vector")

    property sentiment:
        def __get__(self):
            return self.c.sentiment
        def __set__(self, float sentiment):
            self.c.sentiment = sentiment
        
    property orth_:
        def __get__(self):
            return self.vocab.strings[self.c.orth]

    property lower:
        def __get__(self): return self.c.lower
        def __set__(self, int x): self.c.lower = x
    
    property norm:
        def __get__(self): return self.c.norm
        def __set__(self, int x): self.c.norm = x

    property shape:
        def __get__(self): return self.c.shape
        def __set__(self, int x): self.c.shape = x

    property prefix:
        def __get__(self): return self.c.prefix
        def __set__(self, int x): self.c.prefix = x

    property suffix:
        def __get__(self): return self.c.suffix
        def __set__(self, int x): self.c.suffix = x
    
    property cluster:
        def __get__(self): return self.c.cluster
        def __set__(self, int x): self.c.cluster = x
 
    property lang:
        def __get__(self): return self.c.lang
        def __set__(self, int x): self.c.lang = x

    property prob:
        def __get__(self): return self.c.prob
        def __set__(self, float x): self.c.prob = x

    property lower_:
        def __get__(self): return self.vocab.strings[self.c.lower]
        def __set__(self, unicode x): self.c.lower = self.vocab.strings[x]
 
    property norm_:
        def __get__(self): return self.vocab.strings[self.c.norm]
        def __set__(self, unicode x): self.c.norm = self.vocab.strings[x]
    
    property shape_:
        def __get__(self): return self.vocab.strings[self.c.shape]
        def __set__(self, unicode x): self.c.shape = self.vocab.strings[x]

    property prefix_:
        def __get__(self): return self.vocab.strings[self.c.prefix]
        def __set__(self, unicode x): self.c.prefix = self.vocab.strings[x]

    property suffix_:
        def __get__(self): return self.vocab.strings[self.c.suffix]
        def __set__(self, unicode x): self.c.suffix = self.vocab.strings[x]

    property lang_:
        def __get__(self): return self.vocab.strings[self.c.lang]
        def __set__(self, unicode x): self.c.lang = self.vocab.strings[x]

    property flags:
        def __get__(self): return self.c.flags
        def __set__(self, flags_t x): self.c.flags = x

    property is_oov:
        def __get__(self): return Lexeme.c_check_flag(self.c, IS_OOV)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, IS_OOV, x)

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
