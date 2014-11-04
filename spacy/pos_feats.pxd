from .tokens cimport Tokens
from thinc.typedefs cimport atom_t


cpdef enum:
    P2i
    P2c
    P2w
    P2shape
    P2pref
    P2suff
    P2title
    P2upper
    P2oft_title
    P2oft_upper
    P2pos
    P2url
    P2num

    P1i
    P1c
    P1w
    P1shape
    P1pre
    P1suff
    P1title
    P1upper
    P1oft_title
    P1oft_upper
    P1pos
    P1url
    P1num

    N0i
    N0c
    N0w
    N0shape
    N0pref
    N0suff
    N0title
    N0upper
    N0oft_title
    N0oft_upper
    N0pos
    N0url
    N0num

    N1i
    N1c
    N1w
    N1shape
    N1pref
    N1suff
    N1title
    N1upper
    N1oft_title
    N1oft_upper
    N1pos
    N1url
    N1num

    N2i
    N2c
    N2w
    N2shape
    N2pref
    N2suff
    N2title
    N2upper
    N2oft_title
    N2oft_upper
    N2pos
    N2url
    N2num

    P2t
    P1t

    CONTEXT_SIZE



cdef int fill_context(atom_t* context, int i, Tokens tokens) except -1
