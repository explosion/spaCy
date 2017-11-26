# coding: utf8
from __future__ import unicode_literals


_exc = {
    # Slang
    'прив': 'привет',
    'ща': 'сейчас',
    'спс': 'спасибо',
    'пжлст': 'пожалуйста',
    'плиз': 'пожалуйста',
    'лан': 'ладно',
    'ясн': 'ясно',
    'всм': 'всмысле',
    'хош': 'хочешь',
    'оч': 'очень'
}


NORM_EXCEPTIONS = {}

for string, norm in _exc.items():
    NORM_EXCEPTIONS[string] = norm
    NORM_EXCEPTIONS[string.title()] = norm
