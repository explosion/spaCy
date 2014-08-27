from spacy.lang cimport Language
from spacy.word cimport Lexeme
cimport cython


cpdef size_t ALPHA
cpdef size_t DIGIT 
cpdef size_t PUNCT
cpdef size_t SPACE
cpdef size_t LOWER
cpdef size_t UPPER
cpdef size_t TITLE
cpdef size_t ASCII

cpdef size_t OFT_LOWER
cpdef size_t OFT_TITLE
cpdef size_t OFT_UPPER

cpdef size_t PUNCT
cpdef size_t CONJ
cpdef size_t NUM
cpdef size_t N
cpdef size_t DET
cpdef size_t ADP
cpdef size_t ADJ
cpdef size_t ADV
cpdef size_t VERB
cpdef size_t NOUN
cpdef size_t PDT
cpdef size_t POS
cpdef size_t PRON
cpdef size_t PRT

cpdef size_t SIC
cpdef size_t CANON_CASED
cpdef size_t SHAPE
cpdef size_t NON_SPARSE


cdef class English(Language):
    cpdef int _split_one(self, unicode word)


cpdef English EN
