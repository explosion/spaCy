# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ..char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, LIST_CURRENCY
from ..char_classes import LIST_ICONS, ALPHA_LOWER, ALPHA_UPPER, ALPHA, HYPHENS
from ..char_classes import QUOTES, CURRENCY

_units = ('km km² km³ m m² m³ dm dm² dm³ cm cm² cm³ mm mm² mm³ ha µm nm yd in ft '
          'kg g mg µg t lb oz m/s km/h kmh mph hPa Pa mbar mb MB kb KB gb GB tb '
          'TB T G M K км км² км³ м м² м³ дм дм² дм³ см см² см³ мм мм² мм³ нм '
          'кг г мг м/с км/ч кПа Па мбар Кб КБ кб Мб МБ мб Гб ГБ гб Тб ТБ тб')


def merge_chars(char): return char.strip().replace(' ', '|')


UNITS = merge_chars(_units)

_prefixes = (['\'\'', '§', '%', '=', r'\+[0-9]+%',  # 90%
              r'\'([0-9]){2}([\-]\'([0-9]){2})*',  # '12'-13
              r'\-([0-9]){1,9}\.([0-9]){1,9}',  # -12.13
              r'\'([Α-Ωα-ωίϊΐόάέύϋΰήώ]+)\'',  # 'αβγ'
              r'([Α-Ωα-ωίϊΐόάέύϋΰήώ]){1,3}\'',  # αβγ'
              r'http://www.[A-Za-z]+\-[A-Za-z]+(\.[A-Za-z]+)+(\/[A-Za-z]+)*(\.[A-Za-z]+)*',
              r'[ΈΆΊΑ-Ωα-ωίϊΐόάέύϋΰήώ]+\*',  # όνομα*
              r'\$([0-9])+([\,\.]([0-9])+){0,1}',
              ] + LIST_PUNCT + LIST_ELLIPSES + LIST_QUOTES +
             LIST_CURRENCY + LIST_ICONS)

_suffixes = (LIST_PUNCT + LIST_ELLIPSES + LIST_QUOTES + LIST_ICONS +
             [r'(?<=[0-9])\+',  # 12+
              r'([0-9])+\'',  # 12'
              r'([A-Za-z])?\'',  # a'
              r'^([0-9]){1,2}\.',  # 12.
              r' ([0-9]){1,2}\.',  # 12.
              r'([0-9]){1}\) ',  # 12)
              r'^([0-9]){1}\)$',  # 12)
              r'(?<=°[FfCcKk])\.',
              r'([0-9])+\&',  # 12&
              r'(?<=[0-9])(?:{})'.format(CURRENCY),
              r'(?<=[0-9])(?:{})'.format(UNITS),
              r'(?<=[0-9{}{}(?:{})])\.'.format(ALPHA_LOWER, r'²\-\)\]\+', QUOTES),
              r'(?<=[{a}][{a}])\.'.format(a=ALPHA_UPPER),
              r'(?<=[Α-Ωα-ωίϊΐόάέύϋΰήώ])\-',  # όνομα-
              r'(?<=[Α-Ωα-ωίϊΐόάέύϋΰήώ])\.',
              r'^[Α-Ω]{1}\.',
              r'\ [Α-Ω]{1}\.',
              # πρώτος-δεύτερος , πρώτος-δεύτερος-τρίτος
              r'[ΈΆΊΑΌ-Ωα-ωίϊΐόάέύϋΰήώ]+([\-]([ΈΆΊΑΌ-Ωα-ωίϊΐόάέύϋΰήώ]+))+',
              r'([0-9]+)mg',  # 13mg
              r'([0-9]+)\.([0-9]+)m'  # 1.2m
              ])

_infixes = (LIST_ELLIPSES + LIST_ICONS +
            [r'(?<=[0-9])[+\/\-\*^](?=[0-9])',  # 1/2 , 1-2 , 1*2
             r'([a-zA-Z]+)\/([a-zA-Z]+)\/([a-zA-Z]+)',  # name1/name2/name3
             r'([0-9])+(\.([0-9]+))*([\-]([0-9])+)+',  # 10.9 , 10.9.9 , 10.9-6
             r'([0-9])+[,]([0-9])+[\-]([0-9])+[,]([0-9])+',  # 10,11,12
             r'([0-9])+[ης]+([\-]([0-9])+)+',  # 1ης-2
             # 15/2 , 15/2/17 , 2017/2/15
             r'([0-9]){1,4}[\/]([0-9]){1,2}([\/]([0-9]){0,4}){0,1}',
             r'[A-Za-z]+\@[A-Za-z]+(\-[A-Za-z]+)*\.[A-Za-z]+',  # abc@cde-fgh.a
             r'([a-zA-Z]+)(\-([a-zA-Z]+))+',  # abc-abc
             r'(?<=[{}])\.(?=[{}])'.format(ALPHA_LOWER, ALPHA_UPPER),
             r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}])[?";:=,.]*(?:{h})(?=[{a}])'.format(a=ALPHA, h=HYPHENS),
             r'(?<=[{a}"])[:<>=/](?=[{a}])'.format(a=ALPHA)])

TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
