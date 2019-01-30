# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM

import regex

VIJF = 'vijf'
ZES = 'zes'
ZEVEN = 'zeven'
ACHT = 'acht'
NEGEN = 'negen'
TIEN = 'tien'
HONDERD = "honderd"
DUIZEND = "duizend"

wrong_ordinals_re = regex.compile(r"""(?x)
.*(?P<wrong>nulste|eende|tweeste|driede|vierste|vijfste|zeste|zesste|achtde|tienste|honderdde|duizendde)
$""")

hundreds_units_and_tens_thousand_re = regex.compile(r"""(?x)
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
        (?P<en>en)??
        (
          (?P<from_13_to_19>(der|veer|vijf|zes|zeven|acht|negen)
                             tien
          )
          |
          (?:
            (?P<from_1_to_12>  een|twee|drie |vier|vijf|zes|
                             zeven|acht|negen|tien|elf |twaalf
            )
          )
        )
      )*
      (?P<thousand>duizend)*
      (?P<ordinal_1_12>(?<en_ordinal>en)*(?:(?P<ordinal_1>eerste)
                              |
                              (?P<ordinal_3>derde)
                              |
                              (?P<ordinal_8>achtste)
                              |
                              (?P<ordinal_245679_10_11_12>(twee |vier|vijf|zes|zeven|
                                                           negen|tien|elf |twaalf
                                                           )
                                                           de
                              )
                              )$
      )*
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
    m = hundreds_units_and_tens_thousand_re.match(number)
    if m:
        if m.group('ordinal'):
            ordinal = True
        elif m.group('ordinal_1_12'):
            ordinal = True
            if m.group('ordinal_1'):
                value = 1
            elif m.group('ordinal_3'):
                value = 3
            elif m.group('ordinal_8'):
                value = 8
            elif m.group('ordinal_245679_10_11_12'):
                value = text_lookup[m.group('ordinal_245679_10_11_12')]
        else:
            ordinal = False

        if determine_value:
            if m.group('rest'):
                return None, None
            else:
                if m.group('hundreds'):
                    value += 100 * text_lookup[m.group('hundreds')]
                elif m.group('hundred'):
                    value += 100
                if m.group('from_1_to_12'):
                    value += text_lookup[m.group('from_1_to_12')]
                elif m.group('from_13_to_19'):
                    if m.group('en'):
                        return None, None
                    try:
                        value += text_lookup[m.group('from_13_to_19')]
                    except KeyError:
                        # 15 - 19
                        value += 10 + text_lookup[m.group('from_13_to_19').replace('tien', '')]
                if m.group('tens'):
                    value += text_lookup[m.group('tens')]
                if m.group('units'):
                    value += text_lookup[m.group('units')[:-1]]
                if m.group('thousand'):
                    if value:
                        value *= 1000
                    else:
                        value = 1000
                return value, ordinal
        else:
            if m.group('rest') or (m.group('from_13_to_19') and m.group('en')):
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
