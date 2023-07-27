from . cimport symbols


cdef enum attr_id_t:
    NULL_ATTR = 0
    IS_ALPHA = symbols.IS_ALPHA
    IS_ASCII = symbols.IS_ASCII
    IS_DIGIT = symbols.IS_DIGIT
    IS_LOWER = symbols.IS_LOWER
    IS_PUNCT = symbols.IS_PUNCT
    IS_SPACE = symbols.IS_SPACE
    IS_TITLE = symbols.IS_TITLE
    IS_UPPER = symbols.IS_UPPER
    LIKE_URL = symbols.LIKE_URL
    LIKE_NUM = symbols.LIKE_NUM
    LIKE_EMAIL = symbols.LIKE_EMAIL
    IS_STOP = symbols.IS_STOP
    IS_BRACKET = symbols.IS_BRACKET
    IS_QUOTE = symbols.IS_QUOTE
    IS_LEFT_PUNCT = symbols.IS_LEFT_PUNCT
    IS_RIGHT_PUNCT = symbols.IS_RIGHT_PUNCT
    IS_CURRENCY = symbols.IS_CURRENCY

    ID = symbols.ID
    ORTH = symbols.ORTH
    LOWER = symbols.LOWER
    NORM = symbols.NORM
    SHAPE = symbols.SHAPE
    PREFIX = symbols.PREFIX
    SUFFIX = symbols.SUFFIX

    LENGTH = symbols.LENGTH
    CLUSTER = symbols.CLUSTER
    LEMMA = symbols.LEMMA
    POS = symbols.POS
    TAG = symbols.TAG
    DEP = symbols.DEP
    ENT_IOB = symbols.ENT_IOB
    ENT_TYPE = symbols.ENT_TYPE
    HEAD = symbols.HEAD
    SENT_START = symbols.SENT_START
    SPACY = symbols.SPACY
    PROB = symbols.PROB

    LANG = symbols.LANG
    ENT_KB_ID = symbols.ENT_KB_ID
    MORPH = symbols.MORPH
    ENT_ID = symbols.ENT_ID

    IDX = symbols.IDX
