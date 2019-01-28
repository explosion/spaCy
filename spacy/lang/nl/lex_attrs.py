# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM

import re

VIJF = 'vijf'
ZES = 'zes'
ZEVEN = 'zeven'
ACHT = 'acht'
NEGEN = 'negen'
TIEN = 'tien'
HONDERD = "honderd"
DUIZEND = "duizend"

units_and_tens_re = re.compile(
    r"(?P<units>(eene|tweeë|drieë|viere|vijfe|zese|zevene|achte|negene))n(?P<tens>(twin|der|veer|vijf|zes|zeven|tach|negen)tig)")
numeric_lookup = {0:  'nul',
                  1:  'een',
                  2:  'twee',
                  3:  'drie',
                  4:  'vier',
                  5:  VIJF,
                  6:  ZES,
                  7:  ZEVEN,
                  8:  ACHT,
                  9:  NEGEN,
                  10: TIEN,
                  11: 'elf',
                  12: 'twaalf',
                  13: 'dertien',
                  14: 'veertien',
                  20: 'twintig',
                  30: 'dertig',
                  40: 'veertig',
                  50: 'vijftig',
                  60: 'zestig',
                  70: 'zeventig',
                  80: 'tachtig',
                  90: 'negentig',
                  1000000: 'miljoen',
                  1000000000: 'miljard',
                  1000000000000: 'biljoen',
                  1000000000000000: 'biljard',
                  1000000000000000000: 'triljoen',
                  1000000000000000000000: 'triljard',
                  }

text_lookup = {}
for number, text in numeric_lookup.items():
    text_lookup[text] = number


def split_off_hundreds(number):
    # 200 - 999
    for hundreds in range(2, 10):
        x_honderd = numeric_lookup[hundreds] + HONDERD
        if x_honderd in number:
            number = number.replace(x_honderd + "en", "")
            number = number.replace(x_honderd, "")
            break
        else:
            hundreds = 0
    # 100 - 199
    if HONDERD in number:
        honderd = HONDERD
        number = number.replace(honderd + "en", "")
        number = number.replace(honderd, "")
        hundreds = 1
    return hundreds, number


def is_ordinal(number):
    ordinal = False
    n = number
    if number.endswith("ste"):
        ordinal = True
        n = number[:-3]
    elif number.endswith("de"):
        ordinal = True
        n = number[:-2]
    return n, ordinal


def multiple_of_1000(number):
    if number.endswith(DUIZEND):
        k = 1000
        n = number.replace(DUIZEND, "")
    else:
        k = 1
        n = number
    return k, n


def parse_number(number):
    """Accepts Dutch text representing a number which can be written as a single word
       in the range of 0-999 and their multiples of 1 thousand.
       After 'duizend' a space is required
       :param number: text string that may be a number
       :return: a tuple consisting of
                * either None or the value number represents as an int, a float
                  or a string that can be passed to eval()
                * None:  This string cannot be converted to a valid number
                  False: This string represents a cardinal number
                  True:  This string represents an ordinal number"""

    if number == 'nul':
        return 0, False
    elif number == 'nulde':
        return 0, True
    elif number == 'één':
        return 1, False
    elif number == 'eerste':
        return 1, True
    elif number == 'derde':
        return 3, True
    elif number == DUIZEND:
        return 1000, False
    elif number == DUIZEND + 'ste':
        return 1000, True
    elif number == 'driekwart': # '3/4 is the only fraction that can be written in one word in Dutch
        return 0.75, False

    # Can it be an ordinal number?
    number, ordinal = is_ordinal(number)

    # Is it a multiple of 1000?
    k, number = multiple_of_1000(number)

    value = None
    h, number = split_off_hundreds(number)
    if h:
        value = 0

    if number:
        if number in text_lookup:
            # 01 - 14
            value = int(text_lookup[number])
            number = number.replace(number, '')
        elif number.endswith(TIEN):
            # 15 - 19
            unit = number.replace(TIEN, '')
            if unit in [VIJF, ZES, ZEVEN, ACHT, NEGEN]:
                u = text_lookup[unit]
                value = 10 + u
            number = number.replace(unit + TIEN, '')
        if not value:
            ut = units_and_tens_re.match(number)
            if ut:
                # 20 - 99
                t = ut.group('tens')
                u = ut.group('units')[:-1]
                value = text_lookup[t] + text_lookup[u]
                number = number.replace(ut.group('units') + 'n' + t, '')
    if number or not(value or h):
        # If there is still something left in number
        # or no value could be determined for last 2 digits
        # or not a multiple of 100
        return None, None
    return (h*100 + value) * k, ordinal


def like_num(text):
    text = text.replace(',', '').replace('.', '')
    if text.isdigit():
        return True
    if text.count('/') == 1:
        num, denom = text.split('/')
        if num.isdigit() and denom.isdigit():
            return True
    if parse_number(text)[1] is not None:
        return True
    return False


LEX_ATTRS = {
    LIKE_NUM: like_num
}
