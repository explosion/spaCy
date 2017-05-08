# coding: utf8
from __future__ import unicode_literals

import unicodedata
import regex as re


_like_email = re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)').match


def is_alpha(text):
    return text.isalpha()


def is_digit(text):
    return text.isdigit()


def is_punct(text):
    for char in text:
        if not unicodedata.category(char).startswith('P'):
            return False
    return True


def is_space(text):
    return text.isspace()


def is_ascii(text):
    for char in text:
        if ord(char) >= 128:
            return False
    return True


def is_bracket(text):
    brackets = ('(',')','[',']','{','}','<','>')
    return text in brackets


def is_quote(text):
    quotes = ('"',"'",'`','«','»','‘','’','‚','‛','“','”','„','‟','‹','›','❮','❯',"''",'``')
    return text in quotes


def is_left_punct(text):
    left_punct = ('(','[','{','<','"',"'",'«','‘','‚','‛','“','„','‟','‹','❮','``')
    return text in left_punct


def is_right_punct(text):
    right_punct = (')',']','}','>','"',"'",'»','’','”','›','❯',"''")
    return text in right_punct


def is_title(text):
    return text.istitle()


def is_lower(text):
    return text.islower()


def is_upper(text):
    return text.isupper()


def like_email(text):
    return _like_email(text)


def like_url(text):
    TLDs = set('com|org|edu|gov|net|mil|aero|asia|biz|cat|coop|info|int|jobs|'
               'mobi|museum|name|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|'
               'ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|'
               'br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|'
               'cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|'
               'fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|'
               'gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|'
               'jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|'
               'lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|'
               'mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|'
               'ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|'
               'sg|sh|si|sj|sk|sl|sm|sn|so|sr|ss|st|su|sv|sy|sz|tc|td|tf|tg|th|'
               'tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|'
               'vg|vi|vn|vu|wf|ws|ye|yt|za|zm|zw'.split('|'))
    # We're looking for things that function in text like URLs. So, valid URL
    # or not, anything they say http:// is going to be good.
    if text.startswith('http://') or text.startswith('https://'):
        return True
    elif text.startswith('www.') and len(text) >= 5:
        return True
    if text[0] == '.' or text[-1] == '.':
        return False
    for i in range(len(text)):
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


def word_shape(text):
    if len(text) >= 100:
        return 'LONG'
    length = len(text)
    shape = []
    last = ''
    shape_char = ''
    seq = 0
    for char in text:
        if char.isalpha():
            if char.isupper():
                shape_char = 'X'
            else:
                shape_char = 'x'
        elif char.isdigit():
            shape_char = 'd'
        else:
            shape_char = char
        if shape_char == last:
            seq += 1
        else:
            seq = 0
            last = shape_char
        if seq < 4:
            shape.append(shape_char)
    return ''.join(shape)
