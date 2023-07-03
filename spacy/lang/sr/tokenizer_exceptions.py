from ...symbols import NORM, ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

_exc = {}

_abbrev_exc = [
    # Weekdays abbreviations
    {ORTH: "пoн", NORM: "понедељак"},
    {ORTH: "уто", NORM: "уторак"},
    {ORTH: "сре", NORM: "среда"},
    {ORTH: "чет", NORM: "четвртак"},
    {ORTH: "пет", NORM: "петак"},
    {ORTH: "суб", NORM: "субота"},
    {ORTH: "нед", NORM: "недеља"},
    # Months abbreviations
    {ORTH: "јан", NORM: "јануар"},
    {ORTH: "феб", NORM: "фебруар"},
    {ORTH: "мар", NORM: "март"},
    {ORTH: "апр", NORM: "април"},
    {ORTH: "јуни", NORM: "јун"},
    {ORTH: "јули", NORM: "јул"},
    {ORTH: "авг", NORM: "август"},
    {ORTH: "сеп", NORM: "септембар"},
    {ORTH: "септ", NORM: "септембар"},
    {ORTH: "окт", NORM: "октобар"},
    {ORTH: "нов", NORM: "новембар"},
    {ORTH: "дец", NORM: "децембар"},
]


for abbrev_desc in _abbrev_exc:
    abbrev = abbrev_desc[ORTH]
    for orth in (abbrev, abbrev.capitalize(), abbrev.upper()):
        _exc[orth] = [{ORTH: orth, NORM: abbrev_desc[NORM]}]
        _exc[orth + "."] = [{ORTH: orth + ".", NORM: abbrev_desc[NORM]}]


# common abbreviations
_slang_exc = [
    # without dot
    {ORTH: "др", NORM: "доктор"},
    {ORTH: "гдин", NORM: "господин"},
    {ORTH: "гђа", NORM: "госпођа"},
    {ORTH: "гђица", NORM: "госпођица"},
    {ORTH: "мр", NORM: "магистар"},
    {ORTH: "Бгд", NORM: "београд"},
    {ORTH: "цм", NORM: "центиметар"},
    {ORTH: "м", NORM: "метар"},
    {ORTH: "км", NORM: "километар"},
    {ORTH: "мг", NORM: "милиграм"},
    {ORTH: "кг", NORM: "килограм"},
    {ORTH: "дл", NORM: "децилитар"},
    {ORTH: "хл", NORM: "хектолитар"},
    # with dot
    {ORTH: "ул.", NORM: "улица"},
    {ORTH: "бр.", NORM: "број"},
    {ORTH: "нпр.", NORM: "на пример"},
    {ORTH: "тзв.", NORM: "такозван"},
    {ORTH: "проф.", NORM: "професор"},
    {ORTH: "стр.", NORM: "страна"},
    {ORTH: "једн.", NORM: "једнина"},
    {ORTH: "мн.", NORM: "множина"},
    {ORTH: "уч.", NORM: "ученик"},
    {ORTH: "разр.", NORM: "разред"},
    {ORTH: "инж.", NORM: "инжењер"},
    {ORTH: "гимн.", NORM: "гимназија"},
    {ORTH: "год.", NORM: "година"},
    {ORTH: "мед.", NORM: "медицина"},
    {ORTH: "гимн.", NORM: "гимназија"},
    {ORTH: "акад.", NORM: "академик"},
    {ORTH: "доц.", NORM: "доцент"},
    {ORTH: "итд.", NORM: "и тако даље"},
    {ORTH: "и сл.", NORM: "и слично"},
    {ORTH: "н.е.", NORM: "нове ере"},
    {ORTH: "о.г.", NORM: "ове године"},
    {ORTH: "л.к.", NORM: "лична карта"},
    {ORTH: "в.д.", NORM: "вршилац дужности"},
    {ORTH: "стр.", NORM: "страна"},
    # with qoute
    {ORTH: "ал'", NORM: "али"},
    {ORTH: "ил'", NORM: "или"},
    {ORTH: "је л'", NORM: "је ли"},
    {ORTH: "да л'", NORM: "да ли"},
    {ORTH: "држ'те", NORM: "држите"},
]

for slang_desc in _slang_exc:
    _exc[slang_desc[ORTH]] = [slang_desc]


TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
