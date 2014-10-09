# cython: profile=True
# cython: embedsignature=True

from .lexeme cimport lexeme_get_string
from .lexeme cimport lexeme_check_orth_flag, lexeme_check_dist_flag

from .lexeme cimport *


cdef class Lexeme:
    """A lexical type --- a word, punctuation symbol, whitespace sequence, etc
    keyed by a case-sensitive unicode string. All tokens with the same string,
    e.g. all instances of "dog", ",", "NASA" etc should be mapped to the same
    Lexeme.

    You should avoid instantiating Lexemes directly, and instead use the
    :py:meth:`space.lang.Language.tokenize` and :py:meth:`spacy.lang.Language.lookup`
    methods on the global object exposed by the language you're working with,
    e.g. :py:data:`spacy.en.EN`.

    Attributes:
        string (unicode):
            The unicode string.
            
            Implemented as a property; relatively expensive.

        length (size_t):
            The number of unicode code-points in the string.

        prob (double):
            An estimate of the word's unigram log probability.

            Probabilities are calculated from a large text corpus, and smoothed using
            simple Good-Turing.  Estimates are read from data/en/probabilities, and
            can be replaced using spacy.en.load_probabilities.
        
        cluster (size_t):
            An integer representation of the word's Brown cluster.

            A Brown cluster is an address into a binary tree, which gives some (noisy)
            information about the word's distributional context.
    
            >>> strings = (u'pineapple', u'apple', u'dapple', u'scalable')
            >>> print ["{0:b"} % lookup(s).cluster for s in strings]
            ["100111110110", "100111100100", "01010111011001", "100111110110"]

            The clusterings are unideal, but often slightly useful.
            "pineapple" and "apple" share a long prefix, indicating a similar meaning,
            while "dapple" is totally different. On the other hand, "scalable" receives
            the same cluster ID as "pineapple", which is not what we'd like.
    """
    def __cinit__(self, size_t lexeme_addr):
        self._c = <LexemeC*>lexeme_addr

    property string:
        def __get__(self):
            cdef bytes utf8_string = self._c.strings[<int>LexStr_key]
            cdef unicode string = utf8_string.decode('utf8')
            return string

    property prob:
        def __get__(self):
            return self._c.floats[<int>LexFloat_prob]

    property cluster:
        def __get__(self):
            return self._c.ints[<int>LexInt_cluster]

    property length:
        def __get__(self):
            return self._c.ints[<int>LexInt_length]

    cpdef bint check_orth_flag(self, size_t flag_id) except *:
        return lexeme_check_orth_flag(self._c, flag_id)

    cpdef bint check_dist_flag(self, size_t flag_id) except *:
        return lexeme_check_dist_flag(self._c, flag_id)

    cpdef unicode string_view(self, size_t view_id):
        return lexeme_get_string(self._c, view_id)
