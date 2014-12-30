# cython: embedsignature=True
from .. import orth
from ..typedefs cimport flags_t


def get_flags(unicode string):
    cdef flags_t flags = 0
    flags |= orth.is_alpha(string) << IS_ALPHA
    flags |= orth.is_ascii(string) << IS_ASCII
    flags |= orth.is_digit(string) << IS_DIGIT
    flags |= orth.is_lower(string) << IS_LOWER
    flags |= orth.is_punct(string) << IS_PUNCT
    flags |= orth.is_space(string) << IS_SPACE
    flags |= orth.is_title(string) << IS_TITLE
    flags |= orth.is_upper(string) << IS_UPPER
    flags |= orth.like_url(string) << LIKE_URL
    flags |= orth.like_number(string) << LIKE_NUM
    return flags


