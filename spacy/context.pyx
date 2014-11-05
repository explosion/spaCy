from murmurhash.mrmr cimport hash64
from .lexeme cimport *


cdef void _number_token(Token* t, int* n_fields):
    cdef int i = n_fields[0]
    t.i = i; i += 1
    t.c = i; i += 1
    t.w = i; i += 1
    t.shape = i; i += 1
    t.pref = i; i += 1
    t.suff = i; i += 1
    t.oft_title = i; i += 1
    t.oft_upper = i; i += 1
    t.is_alpha = i; i += 1
    t.is_digit = i; i += 1
    t.is_title = i; i += 1
    t.is_upper = i; i += 1

    t.url = i; i += 1
    t.num = i; i += 1

    t.postype = i; i += 1
    t.pos = i; i += 1
    t.ner = i; i += 1

    n_fields[0] = i


cdef int fill_token(Token* t, Lexeme* lex, atom_t pos, atom_t ner):
    t.i = lex.sic
    t.c = lex.cluster
    t.w = lex.norm if (lex.prob != 0 and lex.prob >= -10) else lex.shape
    t.shape = lex.shape
    t.pref = lex.prefix
    t.suff = lex.suffix

    t.oft_title = lex.flags & (1 << OFT_TITLE)
    t.oft_upper = lex.flags & (1 << OFT_UPPER)
    t.is_alpha = lex.flags & (1 << IS_ALPHA)
    t.is_digit = lex.flags & (1 << IS_DIGIT)
    t.is_title = lex.flags & (1 << IS_TITLE)
    t.is_upper = lex.flags & (1 << IS_UPPER)
    t.url = lex.flags & (1 << LIKE_URL)
    t.num = lex.flags & (1 << LIKE_NUMBER)
    t.postype = lex.postype
    t.pos = pos
    t.ner = ner


cdef int _flatten_token(atom_t* context, Token* ids, Token* vals) except -1:
    context[ids.i] = vals.i
    context[ids.c] = vals.c
    context[ids.w] = vals.w
    context[ids.shape] = vals.shape
    context[ids.pref] = vals.pref
    context[ids.suff] = vals.suff
    context[ids.oft_title] = vals.oft_title
    context[ids.oft_upper] = vals.oft_upper
    context[ids.is_alpha] = vals.is_alpha
    context[ids.is_digit] = vals.is_digit
    context[ids.is_title] = vals.is_title
    context[ids.is_upper] = vals.is_upper
    context[ids.url] = vals.url
    context[ids.num] = vals.num
    context[ids.postype] = vals.postype
    context[ids.pos] = vals.pos
    context[ids.ner] = vals.ner


cdef hash_t fill_slots(Slots* s, int i, Tokens tokens) except 0:
    fill_token(&s.P2, tokens.lex[i-2], tokens.pos[i-2], tokens.ner[i-2])
    fill_token(&s.P1, tokens.lex[i-1], tokens.pos[i-1], tokens.ner[i-1])
    fill_token(&s.N0, tokens.lex[i], tokens.pos[i], tokens.ner[i])
    fill_token(&s.N1, tokens.lex[i+1], tokens.pos[i+1], tokens.ner[i+1])
    fill_token(&s.N2, tokens.lex[i+2], tokens.pos[i+2], tokens.ner[i+2])
    return hash64(s, sizeof(Slots), 0)


cdef int fill_flat(atom_t* context, Slots* s) except -1:
    _flatten_token(context, &FIELD_IDS.P2, &s.P2)
    _flatten_token(context, &FIELD_IDS.P1, &s.P1)
    _flatten_token(context, &FIELD_IDS.N0, &s.N0)
    _flatten_token(context, &FIELD_IDS.N1, &s.N1)
    _flatten_token(context, &FIELD_IDS.N2, &s.N2)


N_FIELDS = 0
_number_token(&FIELD_IDS.P2, &N_FIELDS)
_number_token(&FIELD_IDS.P1, &N_FIELDS)
_number_token(&FIELD_IDS.N0, &N_FIELDS)
_number_token(&FIELD_IDS.N1, &N_FIELDS)
_number_token(&FIELD_IDS.N2, &N_FIELDS)
