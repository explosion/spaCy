# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM

import re

units_and_tens_re = re.compile(
    r"(?P<units>(eene|tweeë|drieë|viere|vijfe|zese|zevene|achte|negene))n(?P<tens>(twin|der|veer|vijf|zes|zeven|tach|negen)tig)")
numeric_lookup = {0:  'nul',
                  1:  'een',
                  2:  'twee',
                  3:  'drie',
                  4:  'vier',
                  5:  'vijf',
                  6:  'zes',
                  7:  'zeven',
                  8:  'acht',
                  9:  'negen',
                  10: 'tien',
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
                  1000: 'duizend',
                  1000000: 'miljoen',
                  1000000000: 'miljard',
                  1000000000000: 'biljoen',
                  1000000000000000: 'biljard',
                  1000000000000000000: 'triljoen',
                  1000000000000000000000: 'triljard',
                  }

text_lookup={}
for number, text in numeric_lookup.items():
     text_lookup[text] = number

def split_of_hundreds(number):
    h = 0
    # 200 - 999
    for hundreds in range(2, 10):
        honderd_ = numeric_lookup[hundreds] + "honderd"
        if honderd_ in number:
            number = number.replace(honderd_ + "en", "")
            number = number.replace(honderd_, "")
            h = hundreds
            break
    # 100 - 199
    if 'honderd' in number:
        honderd_ = "honderd"
        number = number.replace(honderd_ + "en", "")
        number = number.replace(honderd_, "")
        h = 1
    return h, number


def parse_number(number: str) -> ([None,int], [None,bool]):
    """Accepts Dutch text representing a number which can be written as a single word
       in the range of 0-999 and their multiples of 1 thousand.
       After 'duizend' a space is required
       :param number: text string that may be a number
       :return: a tuple consisting of
                * either None or the value number represents as an int
                * None:  This string cannot be converted to a valid number
                  False: This string represents a cardinal number
                  True:  This string represents an ordinal number"""

    if number[-3:] in ('tal'):
        return (None, None)
    if number[-4:] in ('maal', 'hoog', 'hoge', 'voud', 'werf', 'poot'):
        return (None, None)
    if number[-5:] in ('jarig', 'delig', 'potig', 'armig', 'benig'):
        return (None, None)
    if number[-6:] in ('jarige', 'delige', 'potige', 'armige', 'benige',
                       'koppig', 'voudig', 'tallig'):
        return (None, None)
    if number[-7:] in ('koppige', 'voudige', 'tallige'):
        return (None, None)
    if number in ['honderdhout', 'honderdman', 'honderdponder', 'honderduit',
                  'duizendblad', 'duizenddingendoekje', 'duizenddollarvis', 'duizenderlei',
                  'duizendguldenkruid', 'duizendklapper', 'duizendknoop',
                  'duizendkunstenaar', 'duizendschoon']:
        return (None, None)

    ordinal = False
    if number == 'één':
        return (1, ordinal)
    elif number == 'nul':
        return (0, ordinal)
    elif number == 'duizend':
        return (1000, ordinal)
    t=0
    u=0
    # Can it be an ordinal number?
    if number.endswith("ste"):
        ordinal = True
        number = number[:-3]
    elif number.endswith("de"):
        ordinal = True
        number = number[:-2]

    # Is it a multiple of 1000?
    if number.endswith("duizend"):
        k = 1000
        number = number.replace("duizend", "")
    else:
        k = 1
    value = None
    h, number = split_of_hundreds(number)
    if h:
        value = 0
    if number:
        if number in text_lookup:
            # 01 - 14
            value = int(text_lookup[number])
            t = int(value/10)
            u = value - t * 10
        elif number.endswith('tien'):
            # 15 - 19
            unit = number.replace('tien','')
            if unit in ['vijf', 'zes', 'zeven', 'acht', 'negen']:
                u = text_lookup[unit]
                t = 1
                value = t * 10 + u
        if not(value):
            ut = units_and_tens_re.match(number)
            if ut:
                # 20 - 99
                t = ut.group('tens')
                u = ut.group('units')[:-1]
                value = text_lookup[t] + text_lookup[u]
    if not(value or h):
        return (None, None)
    return ((h*100 + value) * k, ordinal)


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
