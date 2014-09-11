from libc.stdlib cimport calloc, free, realloc

from spacy.word cimport Lexeme
from spacy.lexeme cimport lexeme_check_flag
from spacy.lexeme cimport lexeme_string_view


cdef class Tokens:
    """A sequence of references to Lexeme objects.

    The Tokens class provides fast and memory-efficient access to lexical features,
    and can efficiently export the data to a numpy array.  Specific languages
    create their own Tokens subclasses, to provide more convenient access to
    language-specific features.

    >>> from spacy.en import EN
    >>> tokens = EN.tokenize('An example sentence.')
    >>> tokens.string(0)
    'An'
    >>> tokens.prob(0) > tokens.prob(1)
    True
    >>> tokens.can_noun(0)
    False
    >>> tokens.can_noun(1)
    True
    """
    def __cinit__(self, size=100):
        assert size >= 1
        self.lexemes = <LexemeC**>calloc(size, sizeof(LexemeC*))
        self.size = size
        self.length = 0

    def append(self, Lexeme lexeme):
        self.push_back(lexeme._c)

    cdef push_back(self, LexemeC* lexeme):
        if (self.size + 1) == self.length:
            self.size *= 2
            self.lexemes = <LexemeC**>realloc(self.lexemes, self.size * sizeof(LexemeC*))
        self.lexemes[self.length] = lexeme
        self.length += 1

    cpdef unicode string(self, size_t i):
        cdef bytes byte_string = self.lexemes[i].string
        return byte_string.decode('utf8')

    cpdef double prob(self, size_t i):
        return self.lexemes[i].prob

    cpdef size_t cluster(self, size_t i):
        return self.lexemes[i].cluster

    cpdef bint check_flag(self, size_t i, size_t flag_id):
        return lexeme_check_flag(self.lexemes[i], flag_id)

    cpdef unicode string_view(self, size_t i, size_t view_id):
        return lexeme_string_view(self.lexemes[i], view_id)
