from cpython.ref cimport Py_INCREF
from cymem.cymem cimport Pool

from libc.string cimport memset

import orth

from .utf8string cimport Utf8Str

OOV_DIST_FLAGS = 0

memset(&EMPTY_LEXEME, 0, sizeof(Lexeme))


def get_flags(unicode string):
    cdef flag_t flags = 0
    flags |= orth.is_alpha(string) << IS_ALPHA
    flags |= orth.is_ascii(string) << IS_ASCII
    flags |= orth.is_digit(string) << IS_DIGIT
    flags |= orth.is_lower(string) << IS_LOWER
    flags |= orth.is_punct(string) << IS_PUNCT
    flags |= orth.is_space(string) << IS_SPACE
    flags |= orth.is_title(string) << IS_TITLE
    flags |= orth.is_upper(string) << IS_UPPER
    return flags


cdef int from_string(Lexeme* lex, unicode string, StringStore store) except -1:
    cdef bytes byte_string = string.encode('utf8')
    cdef Utf8Str* orig_str = store.intern(<char*>byte_string, len(byte_string))
    lex.id = orig_str.i
    lex.cluster = 0
    lex.length = len(string)
    lex.flags = get_flags(string)
    # TODO: Hook this up
    #lex.norm = norm_str.i
    #lex.shape = norm_str.i
    #lex.asciied = asciied_str.i
    #lex.prefix = prefix_str.i
    #lex.suffix = suffix_str.i


cdef int from_dict(Lexeme* lex, dict props, StringStore stroe) except -1:
    pass
