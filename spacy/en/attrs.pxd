from ..attrs cimport FLAG0, FLAG1, FLAG2, FLAG3, FLAG4, FLAG5, FLAG6, FLAG7
from ..attrs cimport FLAG8, FLAG9, FLAG10
from ..attrs cimport SIC as _SIC
from ..attrs cimport SHAPE as _SHAPE
from ..attrs cimport NORM1 as _NORM1
from ..attrs cimport NORM2 as _NORM2
from ..attrs cimport CLUSTER as _CLUSTER
from ..attrs cimport PREFIX as _PREFIX
from ..attrs cimport SUFFIX as _SUFFIX
from ..attrs cimport LEMMA as _LEMMA
from ..attrs cimport POS as _POS


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
    IS_STOP = FLAG10

    SIC = _SIC
    SHAPE = _SHAPE
    LOWER = _NORM1
    NORM2 = _NORM2
    PREFIX = _PREFIX
    SUFFIX = _SUFFIX
    CLUSTER = _CLUSTER
    LEMMA = _LEMMA
    POS = _POS
