from ..attrs cimport FLAG0, FLAG1, FLAG2, FLAG3, FLAG4, FLAG5, FLAG6, FLAG7
from ..attrs cimport FLAG8, FLAG9, FLAG10
from ..attrs cimport ORTH as _ORTH
from ..attrs cimport SHAPE as _SHAPE
from ..attrs cimport LOWER as _LOWER
from ..attrs cimport NORM as _NORM
from ..attrs cimport CLUSTER as _CLUSTER
from ..attrs cimport PREFIX as _PREFIX
from ..attrs cimport SUFFIX as _SUFFIX
from ..attrs cimport LEMMA as _LEMMA
from ..attrs cimport POS as _POS
from ..attrs cimport TAG as _TAG
from ..attrs cimport DEP as _DEP


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

    ORTH = _ORTH
    SHAPE = _SHAPE
    LOWER = _LOWER
    NORM = _NORM
    PREFIX = _PREFIX
    SUFFIX = _SUFFIX
    CLUSTER = _CLUSTER
    LEMMA = _LEMMA
    POS = _POS
    TAG = _TAG
    DEP = _DEP
