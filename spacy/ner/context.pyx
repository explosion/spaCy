from libc.string cimport memset

from murmurhash.mrmr cimport hash64
from ._state cimport entity_is_open
from ..lexeme cimport *


cdef int _fill_token(atom_t* c, Lexeme* lex, atom_t pos):
    c[T_sic] = lex.sic
    c[T_cluster] = lex.cluster
    c[T_norm] = lex.norm if (lex.prob != 0 and lex.prob >= -10) else lex.shape
    c[T_shape] = lex.shape
    c[T_asciied] = lex.asciied
    c[T_prefix] = lex.prefix
    c[T_suffix] = lex.suffix
    c[T_length] = lex.length

    c[T_postype] = lex.postype
    c[T_nertype] = 0
    c[T_sensetype] = 0
    
    c[T_is_alpha] = lex.flags & (1 << IS_ALPHA)
    c[T_is_digit] = lex.flags & (1 << IS_DIGIT)
    c[T_is_lower] = lex.flags & (1 << IS_LOWER)
    c[T_is_punct] = lex.flags & (1 << IS_PUNCT)
    c[T_is_space] = lex.flags & (1 << IS_SPACE)
    c[T_is_title] = lex.flags & (1 << IS_TITLE)
    c[T_is_upper] = lex.flags & (1 << IS_UPPER)
    c[T_like_url] = lex.flags & (1 << LIKE_URL)
    c[T_like_number] = lex.flags & (1 << LIKE_NUMBER)
    c[T_oft_lower] = lex.flags & (1 << OFT_LOWER)
    c[T_oft_title] = lex.flags & (1 << OFT_TITLE)
    c[T_oft_upper] = lex.flags & (1 << OFT_UPPER)

    c[T_in_males] = lex.flags & (1 << IN_MALES)
    c[T_in_females] = lex.flags & (1 << IN_FEMALES)
    c[T_in_surnames] = lex.flags & (1 << IN_SURNAMES)
    c[T_in_places] = lex.flags & (1 << IN_PLACES)
    c[T_in_celebs] = lex.flags & (1 << IN_CELEBS)
    c[T_in_names] = lex.flags & (1 << IN_NAMES)

    c[T_pos] = pos
    c[T_sense] = 0


cdef int _fill_outer_token(atom_t* c, Lexeme* lex, atom_t pos):
    c[0] = lex.sic
    c[1] = lex.cluster
    c[2] = lex.shape
    c[3] = pos


cdef int fill_context(atom_t* context, State* s, Tokens tokens) except -1:
    cdef int i
    for i in range(N_FIELDS):
        context[i] = 0
    i = s.i
    _fill_token(&context[P2_sic], tokens.lex[i-2], tokens.pos[i-2])
    _fill_token(&context[P1_sic], tokens.lex[i-1], tokens.pos[i-1])
    _fill_token(&context[W_sic], tokens.lex[i], tokens.pos[i])
    _fill_token(&context[N1_sic], tokens.lex[i+1], tokens.pos[i+1])
    _fill_token(&context[N2_sic], tokens.lex[i+2], tokens.pos[i+2])

    cdef atom_t[5] ent_vals
    if entity_is_open(s):
        context[E_label] = s.curr.label
        context[E0_sic] = tokens.lex[s.curr.start].sic
        context[E0_cluster] = tokens.lex[s.curr.start].cluster
        context[E0_pos] = tokens.pos[s.curr.start]
        context[E_last_sic] = tokens.lex[s.i-1].sic
        context[E_last_cluster] = tokens.lex[s.i-1].cluster
        context[E_last_pos] = tokens.pos[s.i-1]
        if (s.curr.start + 1) < s.i:
            context[E1_sic] = tokens.lex[s.curr.start+1].sic
            context[E1_cluster] = tokens.lex[s.curr.start+1].cluster
            context[E1_pos] = tokens.pos[s.curr.start+1]
    return 1
