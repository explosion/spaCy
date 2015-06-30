from ..attrs cimport FLAG0, FLAG1, FLAG2, FLAG3, FLAG4, FLAG5, FLAG6, FLAG7
from ..attrs cimport FLAG8, FLAG9, FLAG10, FLAG11, FLAG12, FLAG13, FLAG14
from ..attrs cimport FLAG15, FLAG16, FLAG17, FLAG18, FLAG19, FLAG20, FLAG21
from ..attrs cimport FLAG22, FLAG23, FLAG24, FLAG25, FLAG26, FLAG27, FLAG28
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
 
    EMO_POS = FLAG11
    EMO_NEG = FLAG12

    EMO_ANGER = FLAG13
    EMO_APATE = FLAG14
    EMO_DISGUST = FLAG15
    EMO_FEAR = FLAG16
    EMO_JOY = FLAG17
    EMO_SAD = FLAG18
    EMO_SURPRISE = FLAG19
    EMO_TRUST = FLAG20

    CLR_NONE = FLAG21
    CLR_BLACK = FLAG22
    CLR_BLUE = FLAG23
    CLR_BROWN = FLAG24
    CLR_GREEN = FLAG25
    CLR_GREY = FLAG26
    CLR_ORANGE = FLAG27
    CLR_PURPLE = FLAG28
    CLR_PINK = FLAG29
    CLR_RED = FLAG30
    CLR_WHITE = FLAG31
    CLR_YELLOW = FLAG32

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
