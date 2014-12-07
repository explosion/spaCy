cdef int fill_context(atom_t[N_FIELDS] context, const int i, TokenC* tokens) except -1:
    _fill_from_token(&context[P2_sic], &tokens[i-2])
    _fill_from_token(&context[P1_sic], &tokens[i-1])
    _fill_from_token(&context[W_sic], &tokens[i])
    _fill_from_token(&context[N1_sic], &tokens[i+1])
    _fill_from_token(&context[N2_sic], &tokens[i+2])


cdef inline void _fill_from_token(atom_t[N_FIELDS] context, const TokenC* t) nogil:
    context[0] = t.lex.sic
    context[1] = t.lex.cluster
    context[2] = t.lex.shape
    context[3] = t.lex.prefix
    context[4] = t.lex.suffix
    context[5] = t.pos
    context[6] = t.sense
