# -*- coding: utf8 -*-
# cython: infer_types=True
from __future__ import unicode_literals
import unicodedata
import re


# Binary string features
cpdef bint is_alpha(unicode string):
    return string.isalpha()


cpdef bint is_digit(unicode string):
    return string.isdigit()


cpdef bint is_punct(unicode string):
    for c in string:
        if not unicodedata.category(c).startswith('P'):
            return False
    else:
        return True


cpdef bint is_space(unicode string):
    return string.isspace()


cpdef bint is_ascii(unicode string):
    for c in string:
        if ord(c) >= 128:
            return False
    else:
        return True


cpdef bint is_bracket(unicode string):
    brackets = ('(',')','[',']','{','}','<','>')
    return string in brackets


cpdef bint is_quote(unicode string):
    quotes = ('"',"'",'`','«','»','‘','’','‚','‛','“','”','„','‟','‹','›','❮','❯',"''",'``')
    return string in quotes


cpdef bint is_left_punct(unicode string):
    left_punct = ('(','[','{','<','"',"'",'«','‘','‚','‛','“','„','‟','‹','❮','``')
    return string in left_punct


cpdef bint is_right_punct(unicode string):
    right_punct = (')',']','}','>','"',"'",'»','’','”','›','❯',"''")
    return string in right_punct


cpdef bint is_title(unicode string):
    return string.istitle()


cpdef bint is_lower(unicode string):
    return string.islower()


cpdef bint is_upper(unicode string):
    return string.isupper()


TLDs = set("com|org|edu|gov|net|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|"
        "name|pro|tel|travel|xxx|"
        "ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|"
        "bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|"
        "co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|"
        "fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|"
        "hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|"
        "km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|"
        "mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|"
        "nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|"
        "sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|ss|st|su|sv|sy|sz|tc|td|tf|tg|th|"
        "tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|"
        "wf|ws|ye|yt|za|zm|zw".split('|'))


cpdef bint like_url(unicode string):
    # We're looking for things that function in text like URLs. So, valid URL
    # or not, anything they say http:// is going to be good.
    if string.startswith('http://') or string.startswith('https://'):
        return True
    elif string.startswith('www.') and len(string) >= 5:
        return True
    # No dots? Not URLish enough
    if string[0] == '.' or string[-1] == '.':
        return False
    # This should be a call to "in", but PyPy lacks this function?
    cdef int i
    for i in range(len(string)):
        if string[i] == '.':
            break
    else:
        return False
    tld = string.rsplit('.', 1)[1].split(':', 1)[0]
    if tld.endswith('/'):
        return True

    if tld.isalpha() and tld in TLDs:
        return True
    return False


# TODO: This should live in the language.orth
NUM_WORDS = set('zero one two three four five six seven eight nine ten'
                'eleven twelve thirteen fourteen fifteen sixteen seventeen'
                'eighteen nineteen twenty thirty forty fifty sixty seventy'
                'eighty ninety hundred thousand million billion trillion'
                'quadrillion gajillion bazillion'.split())
cpdef bint like_number(unicode string):
    string = string.replace(',', '')
    string = string.replace('.', '')
    if string.isdigit():
        return True
    if string.count('/') == 1:
        num, denom = string.split('/')
        if like_number(num) and like_number(denom):
            return True
    if string in NUM_WORDS:
        return True
    return False


_like_email = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)").match
cpdef bint like_email(unicode string):
    return _like_email(string)


cpdef unicode word_shape(unicode string):
    if len(string) >= 100:
        return 'LONG'
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
        if seq < 4:
            shape.append(shape_char)
    return ''.join(shape)


# Exceptions --- do not convert these
_uk_us_except = set([
    'our',
    'ours',
    'four',
    'fours',
    'your',
    'yours',
    'hour',
    'hours',
    'course',
    'rise',
])
def uk_to_usa(unicode string):
    if not string.islower():
        return string
    if string in _uk_us_except:
        return string
    our = re.compile(r'ours?$')
    string = our.sub('or', string)

    return string
