from thinc.typedefs cimport atom_t

from ._state cimport State


cdef int fill_context(atom_t* context, State* state) except -1
# Context elements

# Ensure each token's attributes are listed: w, p, c, c6, c4. The order
# is referenced by incrementing the enum...

# Tokens are listed in left-to-right order.
#cdef size_t* SLOTS = [
#    S2w, S1w,
#    S0l0w, S0l2w, S0lw,
#    S0w,
#    S0r0w, S0r2w, S0rw,
#    N0l0w, N0l2w, N0lw,
#    N0w, N1w, N2w, N3w, 0
#]

# NB: The order of the enum is _NOT_ arbitrary!!
cpdef enum:
    S2w
    S2p
    S2c
    S2c4
    S2c6
    S2L

    S1w
    S1p
    S1c
    S1c4
    S1c6
    S1L

    S1rw
    S1rp
    S1rc
    S1rc4
    S1rc6
    S1rL

    S0lw
    S0lp
    S0lc
    S0lc4
    S0lc6
    S0lL

    S0l2w
    S0l2p
    S0l2c
    S0l2c4
    S0l2c6
    S0l2L

    S0w
    S0p
    S0c
    S0c4
    S0c6
    S0L
    
    S0r2w
    S0r2p
    S0r2c
    S0r2c4
    S0r2c6
    S0r2L

    S0rw
    S0rp
    S0rc
    S0rc4
    S0rc6
    S0rL

    N0l2w
    N0l2p
    N0l2c
    N0l2c4
    N0l2c6
    N0l2L

    N0lw
    N0lp
    N0lc
    N0lc4
    N0lc6
    N0lL

    N0w
    N0p
    N0c
    N0c4
    N0c6
    N0L
 
    N1w
    N1p
    N1c
    N1c4
    N1c6
    N1L
    
    N2w
    N2p
    N2c
    N2c4
    N2c6
    N2L
    
    # Misc features at the end
    dist
    N0lv
    S0lv
    S0rv
    S1lv
    S1rv
    
    CONTEXT_SIZE
