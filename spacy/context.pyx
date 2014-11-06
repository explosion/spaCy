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


cdef int fill_token(Token t, Lexeme* lex, atom_t pos, atom_t ner):
    t.sic = lex.sic
    t.cluster = lex.cluster
    t.norm = lex.norm if (lex.prob != 0 and lex.prob >= -10) else lex.shape
    t.shape = lex.shape
    t.asciied = lex.asciied
    t.prefix = lex.prefix
    t.suffix = lex.suffix
    t.length = lex.length

    t.postype = lex.postype
    t.nertype = 0
    t.sensetype = 0
    
    t.is_alpha = lex.flags & (1 << IS_ALPHA)
    t.is_digit = lex.flags & (1 << IS_DIGIT)
    t.is_lower = lex.flags & (1 << IS_LOWER)
    t.is_punct = lex.flags & (1 << IS_PUNCT)
    t.is_space = lex.flags & (1 << IS_SPACE)
    t.is_title = lex.flags & (1 << IS_TITLE)
    t.is_upper = lex.flags & (1 << IS_UPPER)
    t.like_url = lex.flags & (1 << LIKE_URL)
    t.like_number = lex.flags & (1 << LIKE_NUMBER)
    t.oft_lower = lex.flags & (1 << OFT_LOWER)
    t.oft_title = lex.flags & (1 << OFT_TITLE)
    t.oft_upper = lex.flags & (1 << OFT_UPPER)

    t.in_males = lex.flags & (1 << IN_MALES)
    t.in_females = lex.flags & (1 << IN_FEMALES)
    t.in_surnames = lex.flags & (1 << IN_SURNAMES)
    t.in_places = lex.flags & (1 << IN_PLACES)
    t.in_games = lex.flags & (1 << IN_GAMES)
    t.in_celebs = lex.flags & (1 << IN_CELEBS)
    t.in_names = lex.flags & (1 << IN_NAMES)

    t.pos = pos
    t.sense = 0
    t.ner = ner


cdef int _flatten_token(atom_t* context, Token ids, Token vals) except -1:
    context[ids.sic] = vals.sic
    context[ids.cluster] = vals.cluster
    context[ids.norm] = vals.norm
    context[ids.shape] = vals.shape
    context[ids.asciied] = vals.asciied
    context[ids.prefix] = vals.prefix
    context[ids.suffix] = vals.suffix
    context[ids.length] = vals.length

    context[ids.postype] = vals.postype
    context[ids.nertype] = vals.nertype
    context[ids.sensetype] = vals.sensetype

    context[ids.is_alpha] = vals.is_alpha
    context[ids.is_ascii] = vals.is_ascii
    context[ids.is_digit] = vals.is_digit
    context[ids.is_lower] = vals.is_lower
    context[ids.is_punct] = vals.is_punct
    context[ids.is_title] = vals.is_title
    context[ids.is_upper] = vals.is_upper
    context[ids.like_url] = vals.like_url
    context[ids.like_number] = vals.like_number
    context[ids.oft_lower] = vals.oft_lower
    context[ids.oft_title] = vals.oft_title
    context[ids.oft_upper] = vals.oft_upper

    context[ids.in_males] = vals.in_males
    context[ids.in_females] = vals.in_females
    context[ids.in_surnames] = vals.in_surnames
    context[ids.in_places] = vals.in_places
    context[ids.in_games] = vals.in_games
    context[ids.in_celebs] = vals.in_celebs
    context[ids.in_names] = vals.in_names

    context[ids.pos] = vals.pos
    context[ids.sense] = vals.sense
    context[ids.ner] = vals.ner


cdef hash_t fill_slots(Slots s, int i, Tokens tokens) except 0:
    fill_token(s.P4, tokens.lex[i-4], tokens.pos[i-4], tokens.ner[i-4])
    fill_token(s.P3, tokens.lex[i-3], tokens.pos[i-3], tokens.ner[i-3])
    fill_token(s.P2, tokens.lex[i-2], tokens.pos[i-2], tokens.ner[i-2])
    fill_token(s.P1, tokens.lex[i-1], tokens.pos[i-1], tokens.ner[i-1])
    fill_token(s.N0, tokens.lex[i], tokens.pos[i], tokens.ner[i])
    fill_token(s.N1, tokens.lex[i+1], tokens.pos[i+1], tokens.ner[i+1])
    fill_token(s.N2, tokens.lex[i+2], tokens.pos[i+2], tokens.ner[i+2])
    fill_token(s.N3, tokens.lex[i+3], tokens.pos[i+3], tokens.ner[i+3])
    fill_token(s.N4, tokens.lex[i+4], tokens.pos[i+4], tokens.ner[i+4])
    return 1


cdef int fill_flat(atom_t* context, Slots s) except -1:
    _flatten_token(context, FIELD_IDS.P4, s.P4)
    _flatten_token(context, FIELD_IDS.P3, s.P3)
    _flatten_token(context, FIELD_IDS.P2, s.P2)
    _flatten_token(context, FIELD_IDS.P1, s.P1)
    _flatten_token(context, FIELD_IDS.N0, s.N0)
    _flatten_token(context, FIELD_IDS.N1, s.N1)
    _flatten_token(context, FIELD_IDS.N2, s.N2)
    _flatten_token(context, FIELD_IDS.N3, s.N4)
    _flatten_token(context, FIELD_IDS.N4, s.N4)


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
