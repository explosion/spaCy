from thinc.typedefs cimport atom_t

from .lang cimport Language
from .tokens cimport Tokens
from .tokens cimport TokenC


cpdef enum en_person_t:
    NO_PERSON
    FIRST
    SECOND
    THIRD
    NON_THIRD


cpdef enum en_number_t:
    NO_NUMBER
    SINGULAR
    PLURAL
    MASS


cpdef enum en_gender_t:
    NO_GENDER
    MASCULINE
    FEMININE
    NEUTER


cpdef enum en_case_t:
    NO_CASE
    NOMINATIVE
    GENITIVE
    ACCUSATIVE
    REFLEXIVE
    DEMONYM


cpdef enum en_tenspect_t:
    NO_TENSE
    BASE_VERB
    PRESENT
    PAST
    PASSIVE
    ING
    MODAL


cpdef enum misc_t:
    NO_MISC
    COMPARATIVE
    SUPERLATIVE
    RELATIVE
    NAME

    
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


cpdef enum:
    P2_sic
    P2_cluster
    P2_shape
    P2_prefix
    P2_suffix
    P2_pos
    P2_lemma
    P2_pos_type

    P1_sic
    P1_cluster
    P1_shape
    P1_prefix
    P1_suffix
    P1_pos
    P1_lemma
    P1_pos_type

    W_sic
    W_cluster
    W_shape
    W_prefix
    W_suffix
    W_pos
    W_lemma
    W_pos_type

    N1_sic
    N1_cluster
    N1_shape
    N1_prefix
    N1_suffix
    N1_pos
    N1_lemma
    N1_pos_type

    N2_sic
    N2_cluster
    N2_shape
    N2_prefix
    N2_suffix
    N2_pos
    N2_lemma
    N2_pos_type

    N_CONTEXT_FIELDS


cdef class English(Language):
    pass
