from ..typedefs cimport FLAG0, FLAG1, FLAG2, FLAG3, FLAG4, FLAG5, FLAG6, FLAG7
from ..typedefs cimport FLAG8, FLAG9
from ..typedefs cimport ID as _ID
from ..typedefs cimport SIC as _SIC
from ..typedefs cimport SHAPE as _SHAPE
from ..typedefs cimport DENSE as _DENSE
from ..typedefs cimport CLUSTER as _CLUSTER
from ..typedefs cimport SHAPE as _SHAPE
from ..typedefs cimport PREFIX as _PREFIX
from ..typedefs cimport SUFFIX as _SUFFIX
from ..typedefs cimport LEMMA as _LEMMA
from ..typedefs cimport POS as _POS


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
    SHAPE = _SHAPE
    DENSE = _DENSE
    PREFIX = _PREFIX
    SUFFIX = _SUFFIX
    CLUSTER = _CLUSTER
    LEMMA = _LEMMA
    POS = _POS
