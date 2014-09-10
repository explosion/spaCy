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
    def __cinit__(self):
        self.lexemes = []

    cpdef append(self, object lexeme):
        self.lexemes.append(lexeme)

    cpdef unicode string(self, size_t i):
        return self.lexemes[i].string

    cpdef double prob(self, size_t i):
        return self.lexemes[i].prob

    cpdef size_t cluster(self, size_t i):
        return self.lexemes[i].cluster

    cpdef bint check_flag(self, size_t i, size_t flag_id):
        return self.lexemes[i].check_flag(flag_id)

    cpdef unicode string_view(self, size_t i, size_t view_id):
        return self.lexemes[i].string_view(view_id)
