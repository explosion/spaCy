# cython: embedsignature=True
from ..orth cimport is_alpha, is_ascii, is_digit, is_lower, is_punct, is_space
from ..orth cimport is_title, is_upper, like_url, like_number, like_email
from ..typedefs cimport flags_t


def get_flags(unicode string, is_oov=False):
    cdef flags_t flags = 0
    flags |= is_oov << IS_OOV
    flags |= is_alpha(string) << IS_ALPHA
    flags |= is_ascii(string) << IS_ASCII
    flags |= is_digit(string) << IS_DIGIT
    flags |= is_lower(string) << IS_LOWER
    flags |= is_punct(string) << IS_PUNCT
    flags |= is_space(string) << IS_SPACE
    flags |= is_title(string) << IS_TITLE
    flags |= is_upper(string) << IS_UPPER
    flags |= like_url(string) << LIKE_URL
    flags |= like_number(string) << LIKE_NUM
    flags |= like_email(string) << LIKE_EMAIL
    return flags
