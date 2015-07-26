from ..attrs cimport FLAG13, FLAG14
from ..attrs cimport FLAG15, FLAG16, FLAG17, FLAG18, FLAG19, FLAG20, FLAG21
from ..attrs cimport FLAG22, FLAG23, FLAG24, FLAG25, FLAG26, FLAG27, FLAG28
from ..attrs cimport FLAG29,  FLAG30, FLAG31, FLAG32
from ..attrs cimport IS_ALPHA as _IS_ALPHA
from ..attrs cimport IS_DIGIT as _IS_DIGIT
from ..attrs cimport IS_ASCII as _IS_ASCII
from ..attrs cimport IS_LOWER as _IS_LOWER
from ..attrs cimport IS_PUNCT as _IS_PUNCT
from ..attrs cimport IS_SPACE as _IS_SPACE
from ..attrs cimport IS_TITLE as _IS_TITLE
from ..attrs cimport IS_UPPER as _IS_UPPER
from ..attrs cimport IS_OOV as _IS_OOV
from ..attrs cimport LIKE_EMAIL as _LIKE_EMAIL
from ..attrs cimport LIKE_URL as _LIKE_URL
from ..attrs cimport LIKE_NUM as _LIKE_NUM
from ..attrs cimport IS_STOP as _IS_STOP
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
from ..attrs cimport HEAD as _HEAD
from ..attrs cimport ENT_IOB as _ENT_IOB
from ..attrs cimport ENT_TYPE as _ENT_TYPE


cpdef enum:
    IS_ALPHA = _IS_ALPHA
    IS_ASCII = _IS_ASCII
    IS_DIGIT = _IS_DIGIT
    IS_LOWER = _IS_LOWER
    IS_PUNCT = _IS_PUNCT
    IS_SPACE = _IS_SPACE
    IS_TITLE = _IS_TITLE
    IS_UPPER = _IS_UPPER
    LIKE_URL = _LIKE_URL
    LIKE_NUM = _LIKE_NUM
    LIKE_EMAIL = _LIKE_EMAIL
    IS_STOP = _IS_STOP
    IS_OOV = _IS_OOV
 
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
