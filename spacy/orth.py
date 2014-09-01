# -*- coding: utf8 -*-
from __future__ import unicode_literals
import unicodedata

import math

# Binary string features
def is_alpha(string, prob, case_stats, tag_stats):
    return string.isalpha()


def is_digit(string, prob, case_stats, tag_stats):
    return string.isdigit()


def is_punct(string, prob, case_stats, tag_stats):
    for c in string:
        if unicodedata.category(unichr(c)).startswith('P'):
            return True
    else:
        return False


def is_space(string, prob, case_stats, tag_stats):
    return string.isspace()


def is_ascii(string, prob, case_stats, tag_stats):
    for c in string:
        if unichr(c) >= 128:
            return False
    else:
        return True


def is_title(string, prob, case_stats, tag_stats):
    return string.istitle()


def is_lower(string, prob, case_stats, tag_stats):
    return string.islower()


def is_upper(string, prob, case_stats, tag_stats):
    return string.isupper()


# Statistics features
def oft_case(name, thresh):
    def wrapped(string, prob, case_stats, tag_stats):
        return string
    return wrapped


def can_tag(name, thresh):
    def wrapped(string, prob, case_stats, tag_stats):
        return string
    return wrapped


# String features
def canon_case(string, prob, cluster, case_stats, tag_stats):
    upper_pc = case_stats.get('upper', 0.0)
    title_pc = case_stats.get('title', 0.0)
    lower_pc = case_stats.get('lower', 0.0)
    
    if upper_pc >= lower_pc and upper_pc >= title_pc:
        return string.upper()
    elif title_pc >= lower_pc:
        return string.title()
    else:
        return string.lower()


def word_shape(string, *args):
    length = len(string)
    shape = ""
    last = ""
    shape_char = ""
    seq = 0
    for c in string:
        if c.isalpha():
            if c.isupper():
                shape_char = "X"
            else:
                shape_char = "x"
        elif c.isdigit():
            shape_char = "d"
        else:
            shape_char = c
        if shape_char == last:
            seq += 1
        else:
            seq = 0
            last = shape_char
        if seq < 5:
            shape += shape_char
    return shape


def non_sparse(string, prob, cluster, case_stats, tag_stats):
    if is_alpha(string, prob, case_stats, tag_stats):
        return canon_case(string, prob, cluster, case_stats, tag_stats)
    elif prob >= math.log(0.0001):
        return string
    else:
        return word_shape(string, prob, cluster, case_stats, tag_stats)


def asciify(string):
    '''"ASCIIfy" a Unicode string by stripping all umlauts, tildes, etc.''' 
    # Snippet from
    # http://www.physic.ut.ee/~kkannike/english/prog/python/util/asciify/index.html
    # TODO: Rewrite and improve this
    lookup_table = {
        u'“': '"',
        u'”': '"'
    }
    temp = u'' 
    for char in string:
        if char in lookup_table:
            temp += lookup_table[char]
        else:
            decomp = unicodedata.decomposition(char)
            if decomp: # Not an empty string 
                temp += unichr(int(decomp.split()[0], 16))
            else:
                temp += char
    return temp
