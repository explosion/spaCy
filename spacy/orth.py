# -*- coding: utf8 -*-
from __future__ import unicode_literals
import unicodedata
from unidecode import unidecode

import math


TAGS = 'adj adp adv conj det noun num pdt pos pron prt punct verb'.upper().split()


# Binary string features
def is_alpha(string):
    return string.isalpha()


def is_digit(string):
    return string.isdigit()


def is_punct(string):
    for c in string:
        if not unicodedata.category(c).startswith('P'):
            return False
    else:
        return True


def is_space(string):
    return string.isspace()


def is_ascii(string):
    for c in string:
        if ord(c) >= 128:
            return False
    else:
        return True


def is_title(string):
    return string.istitle()


def is_lower(string):
    return string.islower()


def is_upper(string):
    return string.isupper()


# Statistics features
def oft_case(name, thresh):
    def wrapped(string, prob, case_stats, tag_stats):
        return string
    return wrapped


def can_tag(name, thresh=0.5):
    def wrapped(string, prob, case_stats, tag_stats):
        return string
    return wrapped


# String features
def canon_case(string, upper_pc=0.0, title_pc=0.0, lower_pc=0.0):
    if upper_pc >= lower_pc and upper_pc >= title_pc:
        return string.upper()
    elif title_pc >= lower_pc:
        return string.title()
    else:
        return string.lower()


def word_shape(string):
    length = len(string)
    shape = []
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
            shape.append(shape_char)
    return ''.join(shape)


def non_sparse(string, prob, cluster, upper_pc, title_pc, lower_pc):
    if is_alpha(string):
        return canon_case(string, upper_pc, title_pc, lower_pc)
    elif prob >= math.log(0.0001):
        return string
    else:
        return word_shape(string)


def asciied(string):
    ascii_string = unidecode(string)
    return ascii_string.decode('ascii')
