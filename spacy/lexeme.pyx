# cython: embedsignature=True
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
from .attrs cimport IS_OOV


memset(&EMPTY_LEXEME, 0, sizeof(LexemeC))


cdef class Lexeme:
    """An entry in the vocabulary.  A Lexeme has no string context --- it's a
    word-type, as opposed to a word token.  It therefore has no part-of-speech
    tag, dependency parse, or lemma (lemmatization depends on the part-of-speech
    tag).
    """
    def __init__(self, Vocab vocab, int orth):
        self.vocab = vocab
        self.orth = orth
        self.c = <LexemeC*><void*>vocab.get_by_orth(vocab.mem, orth)
        assert self.c.orth == orth

    def set_flag(self, attr_id_t flag_id, bint value):
        Lexeme.c_set_flag(self.c, flag_id, value)
    
    def check_flag(self, attr_id_t flag_id):
        return True if Lexeme.c_check_flag(self.c, flag_id) else False

    def similarity(self, other):
        return numpy.dot(self.vector, other.vector) / (self.vector_norm * other.vector_norm)

    property vector_norm:
        def __get__(self):
            return self.c.l2_norm

        def __set__(self, float value):
            self.c.l2_norm = value

    property vector:
        def __get__(self):
            cdef int length = self.vocab.vector_length
            repvec_view = <float[:length,]>self.c.repvec
            return numpy.asarray(repvec_view)

        def __set__(self, vector):
            assert len(vector) == self.vocab.vector_length
            cdef float value
            for i, value in enumerate(vector):
                self.c.repvec[i] = value

    property repvec:
        def __get__(self):
            return self.vector
        
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

    property like_url:
        def __get__(self): return Lexeme.c_check_flag(self.c, LIKE_URL)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, LIKE_URL, x)
    
    property like_num:
        def __get__(self): return Lexeme.c_check_flag(self.c, LIKE_NUM)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, LIKE_NUM, x)

    property like_email:
        def __get__(self): return Lexeme.c_check_flag(self.c, LIKE_EMAIL)
        def __set__(self, bint x): Lexeme.c_set_flag(self.c, LIKE_EMAIL, x)
