from spacy.lang cimport Language
from spacy.tokens cimport Tokens

# Flags
cpdef enum FlagID:
    IS_ALPHA
    IS_ASCII
    IS_DIGIT
    IS_LOWER
    IS_PUNCT
    IS_SPACE
    IS_TITLE
    IS_UPPER

    LIKE_URL
    LIKE_NUMBER

    OFT_LOWER
    OFT_TITLE
    OFT_UPPER

    IN_MALES
    IN_FEMALES
    IN_SURNAMES
    IN_PLACES
    IN_GAMES
    IN_CELEBS
    IN_NAMES


cdef class English(Language):
    pass
