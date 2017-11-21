# coding: utf8
from __future__ import unicode_literals


_exc = {
    # Slang
    'прив': 'привет',

    # Weekdays abbreviations
    "пн.": "понедельник",
    "вт.": "вторник",
    "ср.": "среда",
    "чт.": "четверг",
    "пт.": "пятница",
    "сб.": "суббота",
    "вс.": "воскресенье",

    # Months abbreviations
    "янв.": "январь",
    "фев.": "февраль",
    "мар.": "март",
    "апр.": "апрель",

}


NORM_EXCEPTIONS = {}

for string, norm in _exc.items():
    NORM_EXCEPTIONS[string] = norm
    NORM_EXCEPTIONS[string.title()] = norm
    if string.endswith('.'):
        NORM_EXCEPTIONS[string[:-1]] = norm
        NORM_EXCEPTIONS[string.title()[:-1]] = norm
