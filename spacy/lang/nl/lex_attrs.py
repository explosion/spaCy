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

wrong_ordinals_re = re.compile(r"""(?x)
.*(?P<wrong>nulste|eende|tweeste|driede|vierste|vijfste|zeste|zesste|achtde|tienste|honderdde|duizendde)
$""")

hundreds_units_and_tens_thousand_re = re.compile(r"""(?x)
      (
        (?P<hundreds>twee|drie|vier|vijf|zes|zeven|acht|negen)honderd
        |
        (?P<hundred>honderd)
      )*
      (
        (?:
          (?P<units>eene|tweeë|drieë|viere|vijfe|zese|zevene|achte|negene)
          n
        )*
        (?P<tens>(twin|der|veer|vijf|zes|zeven|tach|negen)tig)
        |
        (
          (?P<from_13_to_19>(der|veer|vijf|zes|zeven|acht|negen)tien)
          |
          (?:
            (?P<en>en)*
            (?P<from_1_to_12>een|twee|drie|vier|vijf|zes|zeven|acht|negen|tien|elf|twaalf)
          )
        )
      )*
      (?P<thousand>duizend)*
      (?:en)*(?:(?P<ordinal_1>eerste)|(?P<ordinal_3>derde))*
      (?P<ordinal>ste|de)*
      (?P<rest>.*)""")

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


def parse_number(number, determine_value = False):
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

    if number in ['']:
        if determine_value:
            return None, None
        else:
            return False
    elif number == 'nul':
        if determine_value:
            return 0, False
        else:
            return True
    elif number == 'nulde':
        if determine_value:
            return 0, True
        else:
            return True
    elif number == 'één':
        if determine_value:
            return 1, False
        else:
            return True
    elif number == 'driekwart': # '3/4 is the only fraction that can be written in one word in Dutch
        if determine_value:
            return 0.75, False
        else:
            return True
    test_ordinals = wrong_ordinals_re.match(number)
    if test_ordinals and test_ordinals.group('wrong'):
        if determine_value:
            return None, None
        else:
            return False
    value = 0
    ut = hundreds_units_and_tens_thousand_re.match(number)
    if ut:
        if ut.group('ordinal'):
            ordinal = True
        if ut.group('ordinal_1') == 'eerste':
            ordinal = True
            value = 1
        elif ut.group('ordinal_3') == 'derde':
            ordinal = True
            value = 3
        else:
            ordinal = False
        if determine_value:
            if ut.group('rest'):
                return None, None
            else:
                if ut.group('hundreds'):
                    value += 100 * text_lookup[ut.group('hundreds')]
                elif ut.group('hundred'):
                    value += 100
                if ut.group('from_1_to_12'):
                    value += text_lookup[ut.group('from_1_to_12')]
                elif ut.group('from_13_to_19'):
                    if ut.group('from_13_to_19') == 'der':
                        value += 13
                    elif ut.group('from_13_to_19') == 'veer':
                        value += 14
                    else:
                        try:
                            value += text_lookup[ut.group('from_13_to_19')]
                        except KeyError:
                            value += 10 + text_lookup[ut.group('from_13_to_19').replace('tien', '')]
                if ut.group('tens'):
                    value += text_lookup[ut.group('tens')]
                if ut.group('units'):
                    value += text_lookup[ut.group('units')[:-1]]
                if ut.group('thousand'):
                    if value:
                        value *= 1000
                    else:
                        value = 1000
                return value, ordinal
        else:
            if ut.group('rest'):
                return False
            else:
                return True


def like_num(text):
    text = text.replace(',', '').replace('.', '')
    if text.isdigit():
        return True
    if text.count('/') == 1:
        num, denom = text.split('/')
        if num.isdigit() and denom.isdigit():
            return True
    return parse_number(text)


LEX_ATTRS = {
    LIKE_NUM: like_num
}
