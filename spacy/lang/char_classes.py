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
_persian = r'[\p{L}&&\p{Arabic}]'
_russian_lower = r'[ёа-я]'
_russian_upper = r'[ЁА-Я]'
_sinhala = r'[\p{L}&&\p{Sinhala}]'
_tatar_lower = r'[әөүҗңһ]'
_tatar_upper = r'[ӘӨҮҖҢҺ]'
_greek_lower = r'[α-ωάέίόώήύ]'
_greek_upper = r'[Α-ΩΆΈΊΌΏΉΎ]'

_upper = [_latin_upper, _russian_upper, _tatar_upper, _greek_upper]
_lower = [_latin_lower, _russian_lower, _tatar_lower, _greek_lower]
_uncased = [_bengali, _hebrew, _persian, _sinhala]

ALPHA = merge_char_classes(_upper + _lower + _uncased)
ALPHA_LOWER = merge_char_classes(_lower + _uncased)
ALPHA_UPPER = merge_char_classes(_upper + _uncased)

_units = ('km km² km³ m m² m³ dm dm² dm³ cm cm² cm³ mm mm² mm³ ha µm nm yd in ft '
          'kg g mg µg t lb oz m/s km/h kmh mph hPa Pa mbar mb MB kb KB gb GB tb '
          'TB T G M K % км км² км³ м м² м³ дм дм² дм³ см см² см³ мм мм² мм³ нм '
          'кг г мг м/с км/ч кПа Па мбар Кб КБ кб Мб МБ мб Гб ГБ гб Тб ТБ тб'
          'كم كم² كم³ م م² م³ سم سم² سم³ مم مم² مم³ كم غرام جرام جم كغ ملغ كوب اكواب')
_currency = r'\$ £ € ¥ ฿ US\$ C\$ A\$ ₽ ﷼'

# These expressions contain various unicode variations, including characters
# used in Chinese (see #1333, #1340, #1351) – unless there are cross-language
# conflicts, spaCy's base tokenizer should handle all of those by default
_punct = r'… …… , : ; \! \? ¿ ؟ ¡ \( \) \[ \] \{ \} < > _ # \* & 。 ？ ！ ， 、 ； ： ～ · । ، ؛ ٪'
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
