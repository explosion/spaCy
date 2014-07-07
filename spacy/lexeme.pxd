from libc.stdint cimport uint64_t

# Put these above import to avoid circular import problem
ctypedef int ClusterID
ctypedef uint64_t StringHash
ctypedef size_t Lexeme_addr
ctypedef char Bits8
ctypedef uint64_t Bits64


from spacy.spacy cimport Language


cdef struct Orthography:
    StringHash last3
    StringHash shape
    StringHash norm

    Py_UNICODE first
    Bits8 flags


cdef struct Distribution:
    double prob
    ClusterID cluster
    Bits64 tagdict
    Bits8 flags


cdef struct Lexeme:
    StringHash sic # Hash of the original string
    StringHash lex # Hash of the word, with punctuation and clitics split off

    Distribution* dist # Distribution info, lazy loaded
    Orthography* orth  # Extra orthographic views
    Lexeme* tail # Lexemes are linked lists, to deal with sub-tokens


cdef Lexeme BLANK_WORD = Lexeme(0, 0, NULL, NULL, NULL)


cpdef StringHash lex_of(size_t lex_id) except 0
cpdef StringHash norm_of(size_t lex_id) except 0
cpdef StringHash shape_of(size_t lex_id) except 0
#cdef Lexeme* init_lexeme(Language lang, unicode string, StringHash hashed,
#                         int split, size_t length)
                         
 

# Use these to access the Lexeme fields via get_attr(Lexeme*, LexAttr), which
# has a conditional to pick out the correct item.  This allows safe iteration
# over the Lexeme, via:
# for field in range(LexAttr.n): get_attr(Lexeme*, field)
cdef enum HashFields:
    sic
    lex
    normed
    cluster
    n


#cdef uint64_t get_attr(Lexeme* word, HashFields attr)
