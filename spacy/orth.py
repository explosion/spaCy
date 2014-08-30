from __future__ import unicode_literals

# Binary string features
def is_alpha(string, prob, case_stats, tag_stats):
    return False

def is_digit(string, prob, case_stats, tag_stats):
    return False

def is_punct(string, prob, case_stats, tag_stats):
    return False

def is_space(string, prob, case_stats, tag_stats):
    return False

def is_ascii(string, prob, case_stats, tag_stats):
    return False

def is_title(string, prob, case_stats, tag_stats):
    return False

def is_lower(string, prob, case_stats, tag_stats):
    return False

def is_upper(string, prob, case_stats, tag_stats):
    return False


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
    upper_pc = case_stats['upper']
    title_pc = case_stats['title']
    lower_pc = case_stats['lower']
    
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
        if seq < 3:
            shape += shape_char
    return shape


def non_sparse(string, prob, cluster, case_stats, tag_stats):
    return string
