cimport numpy as np

cdef void _set_prefix_lengths(
    const unsigned char* tok_str,
    const int tok_str_l,
    const int p_max_l, 
    unsigned char* pref_l_buf,
) nogil


cdef void _set_suffix_lengths(
    const unsigned char* tok_str,
    const int tok_str_l,
    const int s_max_l, 
    unsigned char* suff_l_buf,
) nogil


cdef int _write_hashes(
    const unsigned char* res_buf,
    const unsigned char* aff_l_buf,
    const unsigned char* offset_buf,
    const int res_buf_last,
    np.uint64_t* hashes_ptr,
) nogil


