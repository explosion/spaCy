from ...symbols import NORM, ORTH

_exc = {}


_abbr_exc = [
    {ORTH: "м", NORM: "метар"},
    {ORTH: "мм", NORM: "милиметар"},
    {ORTH: "цм", NORM: "центиметар"},
    {ORTH: "см", NORM: "сантиметар"},
    {ORTH: "дм", NORM: "дециметар"},
    {ORTH: "км", NORM: "километар"},
    {ORTH: "кг", NORM: "килограм"},
    {ORTH: "дкг", NORM: "декаграм"},
    {ORTH: "дг", NORM: "дециграм"},
    {ORTH: "мг", NORM: "милиграм"},
    {ORTH: "г", NORM: "грам"},
    {ORTH: "т", NORM: "тон"},
    {ORTH: "кл", NORM: "килолитар"},
    {ORTH: "хл", NORM: "хектолитар"},
    {ORTH: "дкл", NORM: "декалитар"},
    {ORTH: "л", NORM: "литар"},
    {ORTH: "дл", NORM: "децилитар"},
]
for abbr in _abbr_exc:
    _exc[abbr[ORTH]] = [abbr]

_abbr_line_exc = [
    {ORTH: "д-р", NORM: "доктор"},
    {ORTH: "м-р", NORM: "магистер"},
    {ORTH: "г-ѓа", NORM: "госпоѓа"},
    {ORTH: "г-ца", NORM: "госпоѓица"},
    {ORTH: "г-дин", NORM: "господин"},
]

for abbr in _abbr_line_exc:
    _exc[abbr[ORTH]] = [abbr]

_abbr_dot_exc = [
    {ORTH: "в.", NORM: "век"},
    {ORTH: "в.д.", NORM: "вршител на должност"},
    {ORTH: "г.", NORM: "година"},
    {ORTH: "г.г.", NORM: "господин господин"},
    {ORTH: "м.р.", NORM: "машки род"},
    {ORTH: "год.", NORM: "женски род"},
    {ORTH: "с.р.", NORM: "среден род"},
    {ORTH: "н.е.", NORM: "наша ера"},
    {ORTH: "о.г.", NORM: "оваа година"},
    {ORTH: "о.м.", NORM: "овој месец"},
    {ORTH: "с.", NORM: "село"},
    {ORTH: "т.", NORM: "точка"},
    {ORTH: "т.е.", NORM: "то ест"},
    {ORTH: "т.н.", NORM: "таканаречен"},
    {ORTH: "бр.", NORM: "број"},
    {ORTH: "гр.", NORM: "град"},
    {ORTH: "др.", NORM: "другар"},
    {ORTH: "и др.", NORM: "и друго"},
    {ORTH: "и сл.", NORM: "и слично"},
    {ORTH: "кн.", NORM: "книга"},
    {ORTH: "мн.", NORM: "множина"},
    {ORTH: "на пр.", NORM: "на пример"},
    {ORTH: "св.", NORM: "свети"},
    {ORTH: "сп.", NORM: "списание"},
    {ORTH: "с.", NORM: "страница"},
    {ORTH: "стр.", NORM: "страница"},
    {ORTH: "чл.", NORM: "член"},
    {ORTH: "арх.", NORM: "архитект"},
    {ORTH: "бел.", NORM: "белешка"},
    {ORTH: "гимн.", NORM: "гимназија"},
    {ORTH: "ден.", NORM: "денар"},
    {ORTH: "ул.", NORM: "улица"},
    {ORTH: "инж.", NORM: "инженер"},
    {ORTH: "проф.", NORM: "професор"},
    {ORTH: "студ.", NORM: "студент"},
    {ORTH: "бот.", NORM: "ботаника"},
    {ORTH: "мат.", NORM: "математика"},
    {ORTH: "мед.", NORM: "медицина"},
    {ORTH: "прил.", NORM: "прилог"},
    {ORTH: "прид.", NORM: "придавка"},
    {ORTH: "сврз.", NORM: "сврзник"},
    {ORTH: "физ.", NORM: "физика"},
    {ORTH: "хем.", NORM: "хемија"},
    {ORTH: "пр. н.", NORM: "природни науки"},
    {ORTH: "истор.", NORM: "историја"},
    {ORTH: "геогр.", NORM: "географија"},
    {ORTH: "литер.", NORM: "литература"},
]

for abbr in _abbr_dot_exc:
    _exc[abbr[ORTH]] = [abbr]


TOKENIZER_EXCEPTIONS = _exc
