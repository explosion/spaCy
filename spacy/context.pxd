from thinc.typedefs cimport atom_t
from .tokens cimport TokenC


cpdef enum:
    P2_sic
    P2_cluster
    P2_shape
    P2_prefix
    P2_suffix
    P2_pos
    P2_sense

    P1_sic
    P1_cluster
    P1_shape
    P1_prefix
    P1_suffix
    P1_pos
    P1_sense

    W_sic
    W_cluster
    W_shape
    W_prefix
    W_suffix
    W_pos
    W_sense

    N1_sic
    N1_cluster
    N1_shape
    N1_prefix
    N1_suffix
    N1_pos
    N1_sense

    N2_sic
    N2_cluster
    N2_shape
    N2_prefix
    N2_suffix
    N2_pos
    N2_sense

    N_FIELDS


cdef int fill_context(atom_t[N_FIELDS] context, const int i, TokenC* tokens) except -1
