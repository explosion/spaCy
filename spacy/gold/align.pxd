cdef class Alignment:
    cdef public object cost
    cdef public object i2j
    cdef public object j2i
    cdef public object i2j_multi
    cdef public object j2i_multi
    cdef public object cand_to_gold
    cdef public object gold_to_cand
