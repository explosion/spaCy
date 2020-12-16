# encoding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM


_exc = {}

_abbrev_exc = [
    # Weekdays abbreviations
    {ORTH: "пoн", LEMMA: "понедељак", NORM: "понедељак"},
    {ORTH: "уто", LEMMA: "уторак", NORM: "уторак"},
    {ORTH: "сре", LEMMA: "среда", NORM: "среда"},
    {ORTH: "чет", LEMMA: "четвртак", NORM: "четвртак"},
    {ORTH: "пет", LEMMA: "петак", NORM: "петак"},
    {ORTH: "суб", LEMMA: "субота", NORM: "субота"},
    {ORTH: "нед", LEMMA: "недеља", NORM: "недеља"},
    # Months abbreviations
    {ORTH: "јан", LEMMA: "јануар", NORM: "јануар"},
    {ORTH: "феб", LEMMA: "фебруар", NORM: "фебруар"},
    {ORTH: "мар", LEMMA: "март", NORM: "март"},
    {ORTH: "апр", LEMMA: "април", NORM: "април"},
    {ORTH: "јуни", LEMMA: "јун", NORM: "јун"},
    {ORTH: "јули", LEMMA: "јул", NORM: "јул"},
    {ORTH: "авг", LEMMA: "август", NORM: "август"},
    {ORTH: "сеп", LEMMA: "септембар", NORM: "септембар"},
    {ORTH: "септ", LEMMA: "септембар", NORM: "септембар"},
    {ORTH: "окт", LEMMA: "октобар", NORM: "октобар"},
    {ORTH: "нов", LEMMA: "новембар", NORM: "новембар"},
    {ORTH: "дец", LEMMA: "децембар", NORM: "децембар"},
]


for abbrev_desc in _abbrev_exc:
    abbrev = abbrev_desc[ORTH]
    for orth in (abbrev, abbrev.capitalize(), abbrev.upper()):
        _exc[orth] = [{ORTH: orth, LEMMA: abbrev_desc[LEMMA], NORM: abbrev_desc[NORM]}]
        _exc[orth + "."] = [
            {ORTH: orth + ".", LEMMA: abbrev_desc[LEMMA], NORM: abbrev_desc[NORM]}
        ]


# common abbreviations
_slang_exc = [
    # without dot
    {ORTH: "др", LEMMA: "доктор", NORM: "доктор"},
    {ORTH: "гдин", LEMMA: "господин", NORM: "господин"},
    {ORTH: "гђа", LEMMA: "госпођа", NORM: "госпођа"},
    {ORTH: "гђица", LEMMA: "госпођица", NORM: "госпођица"},
    {ORTH: "мр", LEMMA: "магистар", NORM: "магистар"},
    {ORTH: "Бгд", LEMMA: "Београд", NORM: "београд"},
    {ORTH: "цм", LEMMA: "центиметар", NORM: "центиметар"},
    {ORTH: "м", LEMMA: "метар", NORM: "метар"},
    {ORTH: "км", LEMMA: "километар", NORM: "километар"},
    {ORTH: "мг", LEMMA: "милиграм", NORM: "милиграм"},
    {ORTH: "кг", LEMMA: "килограм", NORM: "килограм"},
    {ORTH: "дл", LEMMA: "децилитар", NORM: "децилитар"},
    {ORTH: "хл", LEMMA: "хектолитар", NORM: "хектолитар"},
    # with dot
    {ORTH: "ул.", LEMMA: "улица", NORM: "улица"},
    {ORTH: "бр.", LEMMA: "број", NORM: "број"},
    {ORTH: "нпр.", LEMMA: "на пример", NORM: "на пример"},
    {ORTH: "тзв.", LEMMA: "такозван", NORM: "такозван"},
    {ORTH: "проф.", LEMMA: "професор", NORM: "професор"},
    {ORTH: "стр.", LEMMA: "страна", NORM: "страна"},
    {ORTH: "једн.", LEMMA: "једнина", NORM: "једнина"},
    {ORTH: "мн.", LEMMA: "множина", NORM: "множина"},
    {ORTH: "уч.", LEMMA: "ученик", NORM: "ученик"},
    {ORTH: "разр.", LEMMA: "разред", NORM: "разред"},
    {ORTH: "инж.", LEMMA: "инжењер", NORM: "инжењер"},
    {ORTH: "гимн.", LEMMA: "гимназија", NORM: "гимназија"},
    {ORTH: "год.", LEMMA: "година", NORM: "година"},
    {ORTH: "мед.", LEMMA: "медицина", NORM: "медицина"},
    {ORTH: "гимн.", LEMMA: "гимназија", NORM: "гимназија"},
    {ORTH: "акад.", LEMMA: "академик", NORM: "академик"},
    {ORTH: "доц.", LEMMA: "доцент", NORM: "доцент"},
    {ORTH: "итд.", LEMMA: "и тако даље", NORM: "и тако даље"},
    {ORTH: "и сл.", LEMMA: "и слично", NORM: "и слично"},
    {ORTH: "н.е.", LEMMA: "нова ера", NORM: "нове ере"},
    {ORTH: "о.г.", LEMMA: "ова година", NORM: "ове године"},
    {ORTH: "л.к.", LEMMA: "лична карта", NORM: "лична карта"},
    {ORTH: "в.д.", LEMMA: "вршилац дужности", NORM: "вршилац дужности"},
    {ORTH: "стр.", LEMMA: "страна", NORM: "страна"},
    # with qoute
    {ORTH: "ал'", LEMMA: "али", NORM: "али"},
    {ORTH: "ил'", LEMMA: "или", NORM: "или"},
    {ORTH: "је л'", LEMMA: "је ли", NORM: "је ли"},
    {ORTH: "да л'", LEMMA: "да ли", NORM: "да ли"},
    {ORTH: "држ'те", LEMMA: "држати", NORM: "држите"},
]

for slang_desc in _slang_exc:
    _exc[slang_desc[ORTH]] = [slang_desc]


TOKENIZER_EXCEPTIONS = _exc
