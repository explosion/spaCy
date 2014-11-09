from murmurhash.mrmr cimport hash64
from .lexeme cimport *


cdef class Slots:
    def __init__(self):
        self.P4 = Token()
        self.P3 = Token()
        self.P2 = Token()
        self.P1 = Token()
        self.N0 = Token()
        self.N1 = Token()
        self.N2 = Token()
        self.N3 = Token()
        self.N4 = Token()


cdef void _number_token(Token t, int* n_fields):
    cdef int i = n_fields[0]
    t.sic = i; i += 1
    t.cluster = i; i += 1
    t.norm = i; i += 1
    t.shape = i; i += 1
    t.prefix = i; i += 1
    t.suffix = i; i += 1
    t.length = i; i += 1

    t.postype = i; i += 1
    t.nertype = i; i += 1
    t.sensetype = i; i += 1

    t.is_alpha = i; i += 1
    t.is_ascii = i; i += 1
    t.is_digit = i; i += 1
    t.is_lower = i; i += 1
    t.is_punct = i; i += 1
    t.is_space = i; i += 1
    t.is_title = i; i += 1
    t.is_upper = i; i += 1

    t.like_number = i; i += 1
    t.like_url = i; i += 1

    t.oft_lower = i; i += 1
    t.oft_title = i; i += 1
    t.oft_upper = i; i += 1

    t.in_males = i; i += 1
    t.in_females = i; i += 1
    t.in_surnames = i; i += 1
    t.in_places = i; i += 1
    t.in_games = i; i += 1
    t.in_celebs = i; i += 1
    t.in_names = i; i += 1

    t.pos = i; i += 1
    t.sense = i; i += 1
    t.ner = i; i += 1

    n_fields[0] = i


cdef int _fill_token(atom_t* c, Token t, Lexeme* lex, atom_t pos, atom_t ner):
    c[t.sic] = lex.sic
    c[t.cluster] = lex.cluster
    c[t.norm] = lex.norm if (lex.prob != 0 and lex.prob >= -10) else lex.shape
    c[t.shape] = lex.shape
    c[t.asciied] = lex.asciied
    c[t.prefix] = lex.prefix
    c[t.suffix] = lex.suffix
    c[t.length] = lex.length

    c[t.postype] = lex.postype
    c[t.nertype] = 0
    c[t.sensetype] = 0
    
    c[t.is_alpha] = lex.flags & (1 << IS_ALPHA)
    c[t.is_digit] = lex.flags & (1 << IS_DIGIT)
    c[t.is_lower] = lex.flags & (1 << IS_LOWER)
    c[t.is_punct] = lex.flags & (1 << IS_PUNCT)
    c[t.is_space] = lex.flags & (1 << IS_SPACE)
    c[t.is_title] = lex.flags & (1 << IS_TITLE)
    c[t.is_upper] = lex.flags & (1 << IS_UPPER)
    c[t.like_url] = lex.flags & (1 << LIKE_URL)
    c[t.like_number] = lex.flags & (1 << LIKE_NUMBER)
    c[t.oft_lower] = lex.flags & (1 << OFT_LOWER)
    c[t.oft_title] = lex.flags & (1 << OFT_TITLE)
    c[t.oft_upper] = lex.flags & (1 << OFT_UPPER)

    c[t.in_males] = lex.flags & (1 << IN_MALES)
    c[t.in_females] = lex.flags & (1 << IN_FEMALES)
    c[t.in_surnames] = lex.flags & (1 << IN_SURNAMES)
    c[t.in_places] = lex.flags & (1 << IN_PLACES)
    c[t.in_games] = lex.flags & (1 << IN_GAMES)
    c[t.in_celebs] = lex.flags & (1 << IN_CELEBS)
    c[t.in_names] = lex.flags & (1 << IN_NAMES)

    c[t.pos] = pos
    c[t.sense] = 0
    c[t.ner] = ner


cdef int fill_context(atom_t* context, int i, Tokens tokens) except -1:
    _fill_token(context, FIELD_IDS.P4, tokens.lex[i-4], tokens.pos[i-4], tokens.ner[i-4])
    _fill_token(context, FIELD_IDS.P3, tokens.lex[i-3], tokens.pos[i-3], tokens.ner[i-3])
    _fill_token(context, FIELD_IDS.P2, tokens.lex[i-2], tokens.pos[i-2], tokens.ner[i-2])
    _fill_token(context, FIELD_IDS.P1, tokens.lex[i-1], tokens.pos[i-1], tokens.ner[i-1])
    _fill_token(context, FIELD_IDS.N0, tokens.lex[i], tokens.pos[i], tokens.ner[i])
    _fill_token(context, FIELD_IDS.N1, tokens.lex[i+1], tokens.pos[i+1], tokens.ner[i+1])
    _fill_token(context, FIELD_IDS.N2, tokens.lex[i+2], tokens.pos[i+2], tokens.ner[i+2])
    _fill_token(context, FIELD_IDS.N3, tokens.lex[i+3], tokens.pos[i+3], tokens.ner[i+3])
    _fill_token(context, FIELD_IDS.N4, tokens.lex[i+4], tokens.pos[i+4], tokens.ner[i+4])
    return 1


N_FIELDS = 0
FIELD_IDS = Slots()
_number_token(FIELD_IDS.P4, &N_FIELDS)
_number_token(FIELD_IDS.P3, &N_FIELDS)
_number_token(FIELD_IDS.P2, &N_FIELDS)
_number_token(FIELD_IDS.P1, &N_FIELDS)
_number_token(FIELD_IDS.N0, &N_FIELDS)
_number_token(FIELD_IDS.N1, &N_FIELDS)
_number_token(FIELD_IDS.N2, &N_FIELDS)
_number_token(FIELD_IDS.N3, &N_FIELDS)
_number_token(FIELD_IDS.N4, &N_FIELDS)
