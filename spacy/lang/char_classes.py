# coding: utf8
from __future__ import unicode_literals

import regex as re


re.DEFAULT_VERSION = re.VERSION1
merge_char_classes = lambda classes: '[{}]'.format('||'.join(classes))
split_chars = lambda char: list(char.strip().split(' '))
merge_chars = lambda char: char.strip().replace(' ', '|')


_bengali = r'[\p{L}&&\p{Bengali}]'
_hebrew = r'[\p{L}&&\p{Hebrew}]'
_latin_lower = r'[\p{Ll}&&\p{Latin}]'
_latin_upper = r'[\p{Lu}&&\p{Latin}]'
_latin = r'[[\p{Ll}||\p{Lu}]&&\p{Latin}]'

_upper = [_latin_upper]
_lower = [_latin_lower]
_uncased = [_bengali, _hebrew]

ALPHA = merge_char_classes(_upper + _lower + _uncased)
ALPHA_LOWER = merge_char_classes(_lower + _uncased)
ALPHA_UPPER = merge_char_classes(_upper + _uncased)


_units = ('km km² km³ m m² m³ dm dm² dm³ cm cm² cm³ mm mm² mm³ ha µm nm yd in ft '
          'kg g mg µg t lb oz m/s km/h kmh mph hPa Pa mbar mb MB kb KB gb GB tb '
          'TB T G M K %')
_currency = r'\$ £ € ¥ ฿ US\$ C\$ A\$'

# These expressions contain various unicode variations, including characters
# used in Chinese (see #1333, #1340, #1351) – unless there are cross-language
# conflicts, spaCy's base tokenizer should handle all of those by default
_punct = r'… …… , : ; \! \? ¿ ¡ \( \) \[ \] \{ \} < > _ # \* & 。 ？ ！ ， 、 ； ： ～ · ।'
_quotes = r'\' \'\' " ” “ `` ` ‘ ´ ‘‘ ’’ ‚ , „ » « 「 」 『 』 （ ） 〔 〕 【 】 《 》 〈 〉'
_hyphens = '- – — -- --- —— ~'

# Various symbols like dingbats, but also emoji
# Details: https://www.compart.com/en/unicode/category/So
_other_symbols = r'[\p{So}]'


UNITS = merge_chars(_units)
CURRENCY = merge_chars(_currency)
QUOTES = merge_chars(_quotes)
PUNCT = merge_chars(_punct)
HYPHENS = merge_chars(_hyphens)
ICONS = _other_symbols

LIST_UNITS = split_chars(_units)
LIST_CURRENCY = split_chars(_currency)
LIST_QUOTES = split_chars(_quotes)
LIST_PUNCT = split_chars(_punct)
LIST_HYPHENS = split_chars(_hyphens)
LIST_ELLIPSES = [r'\.\.+', '…']
LIST_ICONS = [_other_symbols]
