from ..lexeme cimport FLAG0, FLAG1, FLAG2, FLAG3, FLAG4, FLAG5, FLAG6, FLAG7
from ..lexeme cimport FLAG8, FLAG9
from ..lexeme cimport ID as _ID
from ..lexeme cimport SIC as _SIC
from ..lexeme cimport SHAPE as _SHAPE
from ..lexeme cimport DENSE as _DENSE
from ..lexeme cimport SHAPE as _SHAPE
from ..lexeme cimport PREFIX as _PREFIX
from ..lexeme cimport SUFFIX as _SUFFIX
from ..lexeme cimport LEMMA as _LEMMA


# Work around the lack of global cpdef variables
cpdef enum:
    IS_ALPHA = FLAG0
    IS_ASCII = FLAG1
    IS_DIGIT = FLAG2
    IS_LOWER = FLAG3
    IS_PUNCT = FLAG4
    IS_SPACE = FLAG5
    IS_TITLE = FLAG6
    IS_UPPER = FLAG7
    LIKE_URL = FLAG8
    LIKE_NUM = FLAG9

    ID = _ID
    SIC = _SIC
    SHAPE = _DENSE
    DENSE = _SHAPE
    PREFIX = _PREFIX
    SUFFIX = _SUFFIX
    LEMMA = _LEMMA
