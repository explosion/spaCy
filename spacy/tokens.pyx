# cython: profile=True
from libc.stdlib cimport calloc, free, realloc

from spacy.word cimport Lexeme
from spacy.lexeme cimport lexeme_check_flag
from spacy.lexeme cimport lexeme_string_view


cdef enum Flags:
    Flag_IsAlpha
    Flag_IsAscii
    Flag_IsDigit
    Flag_IsLower
    Flag_IsPunct
    Flag_IsSpace
    Flag_IsTitle
    Flag_IsUpper

    Flag_CanAdj
    Flag_CanAdp
    Flag_CanAdv
    Flag_CanConj
    Flag_CanDet
    Flag_CanNoun
    Flag_CanNum
    Flag_CanPdt
    Flag_CanPos
    Flag_CanPron
    Flag_CanPrt
    Flag_CanPunct
    Flag_CanVerb

    Flag_OftLower
    Flag_OftTitle
    Flag_OftUpper
    Flag_N


cdef enum Views:
    View_CanonForm
    View_WordShape
    View_NonSparse
    View_Asciied
    View_N


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
    def __cinit__(self, string_length=0):
        size = int(string_length / 3) if string_length >= 3 else 1
        self.lexemes = <LexemeC**>calloc(size, sizeof(LexemeC*))
        self.size = size
        self.length = 0

    def __dealloc__(self):
        free(self.lexemes)

    def __getitem__(self, i):
        if i >= self.length:
            raise IndexError
        return Lexeme(<size_t>self.lexemes[i])

    def __len__(self):
        return self.length

    def append(self, Lexeme lexeme):
        self.push_back(lexeme._c)

    cdef int push_back(self, LexemeC* lexeme) except -1:
        if (self.length + 1) == self.size:
            self.size *= 2
            self.lexemes = <LexemeC**>realloc(self.lexemes, self.size * sizeof(LexemeC*))
        self.lexemes[self.length] = lexeme
        self.length += 1

    cpdef unicode string(self, size_t i):
        cdef bytes utf8_string = self.lexemes[i].string[:self.lexemes[i].length]
        cdef unicode string = utf8_string.decode('utf8')
        return string

    cpdef size_t id(self, size_t i):
        return id(self.lexemes[i].string)

    cpdef double prob(self, size_t i):
        return self.lexemes[i].prob

    cpdef size_t cluster(self, size_t i):
        return self.lexemes[i].cluster

    cpdef bint check_flag(self, size_t i, size_t flag_id):
        return lexeme_check_flag(self.lexemes[i], flag_id)

    cpdef unicode string_view(self, size_t i, size_t view_id):
        return lexeme_string_view(self.lexemes[i], view_id)

    # Provide accessor methods for the features supported by the language.
    # Without these, clients have to use the underlying string_view and check_flag
    # methods, which requires them to know the IDs.
    cpdef unicode canon_string(self, size_t i):
        return lexeme_string_view(self.lexemes[i], View_CanonForm)

    cpdef unicode shape_string(self, size_t i):
        return lexeme_string_view(self.lexemes[i], View_WordShape)

    cpdef unicode non_sparse_string(self, size_t i):
        return lexeme_string_view(self.lexemes[i], View_NonSparse)

    cpdef unicode asciied_string(self, size_t i):
        return lexeme_string_view(self.lexemes[i], View_Asciied)

    cpdef size_t canon(self, size_t i):
        return id(self.lexemes[i].views[<size_t>View_CanonForm])

    cpdef size_t shape(self, size_t i):
        return id(self.lexemes[i].views[<size_t>View_WordShape])

    cpdef size_t non_sparse(self, size_t i):
        return id(self.lexemes[i].views[<size_t>View_NonSparse])

    cpdef size_t asciied(self, size_t i):
        return id(self.lexemes[i].views[<size_t>View_Asciied])
    
    cpdef bint is_alpha(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsAlpha)

    cpdef bint is_ascii(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsAscii)

    cpdef bint is_digit(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsDigit)

    cpdef bint is_lower(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsLower)

    cpdef bint is_punct(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsPunct)

    cpdef bint is_space(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsSpace)

    cpdef bint is_title(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsTitle)

    cpdef bint is_upper(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_IsUpper)

    cpdef bint can_adj(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanAdj)

    cpdef bint can_adp(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanAdp)

    cpdef bint can_adv(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanAdv)

    cpdef bint can_conj(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanConj)

    cpdef bint can_det(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanDet)

    cpdef bint can_noun(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanNoun)

    cpdef bint can_num(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanNum)

    cpdef bint can_pdt(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanPdt)

    cpdef bint can_pos(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanPos)

    cpdef bint can_pron(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanPron)

    cpdef bint can_prt(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanPrt)

    cpdef bint can_punct(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanPunct)

    cpdef bint can_verb(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_CanVerb)

    cpdef bint oft_lower(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_OftLower)

    cpdef bint oft_title(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_OftTitle)

    cpdef bint oft_upper(self, size_t i):
        return lexeme_check_flag(self.lexemes[i], Flag_OftUpper)


