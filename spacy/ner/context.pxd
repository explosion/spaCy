from thinc.typedefs cimport atom_t
from ..typedefs cimport hash_t
from ..tokens cimport Tokens
from ..lexeme cimport Lexeme
from .structs cimport State


cpdef enum:
    T_sic
    T_cluster
    T_norm
    T_shape
    T_asciied
    T_prefix
    T_suffix
    T_length
    T_postype
    T_nertype
    T_sensetype
    T_is_alpha
    T_is_ascii
    T_is_digit
    T_is_lower
    T_is_punct
    T_is_space
    T_is_title
    T_is_upper
    T_like_url
    T_like_number
    T_oft_lower
    T_oft_title
    T_oft_upper
    T_in_males
    T_in_females
    T_in_surnames
    T_in_places
    T_in_celebs
    T_in_names
    T_pos
    T_sense
    T_ner


cpdef enum:
    P2_sic
    P2_cluster
    P2_norm
    P2_shape
    P2_prefix
    P2_suffix
    P2_length
    P2_postype
    P2_is_alpha
    P2_is_digit
    P2_is_lower
    P2_is_punct
    P2_is_title
    P2_is_upper
    P2_like_number
    P2_pos

    P1_sic
    P1_cluster
    P1_norm
    P1_shape
    P1_prefix
    P1_suffix
    P1_length
    P1_postype
    P1_is_alpha
    P1_is_digit
    P1_is_lower
    P1_is_punct
    P1_is_title
    P1_is_upper
    P1_like_number
    P1_pos

    W_sic
    W_cluster
    W_norm
    W_shape
    W_prefix
    W_suffix
    W_length
    W_postype
    W_is_alpha
    W_is_digit
    W_is_lower
    W_is_punct
    W_is_space
    W_is_title
    W_is_upper
    W_like_number
    W_pos

    N1_sic
    N1_cluster
    N1_norm
    N1_shape
    N1_prefix
    N1_suffix
    N1_length
    N1_postype
    N1_is_alpha
    N1_is_ascii
    N1_is_digit
    N1_is_lower
    N1_is_punct
    N1_is_space
    N1_is_title
    N1_is_upper
    N1_like_number
    N1_pos

    N2_sic
    N2_cluster
    N2_norm
    N2_shape
    N2_asciied
    N2_prefix
    N2_suffix
    N2_length
    N2_postype
    N2_is_alpha
    N2_is_digit
    N2_is_lower
    N2_is_punct
    N2_is_space
    N2_is_title
    N2_is_upper
    N2_like_number
    N2_pos
    N2_sense

    E_label

    E0_sic
    E0_cluster
    E0_pos

    E1_sic
    E1_cluster
    E1_pos

    E_last_sic
    E_last_cluster
    E_last_pos

    N_FIELDS


cdef int fill_context(atom_t* context, State* s, Tokens tokens) except -1


