# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, TAG, NORM, PRON_LEMMA


_exc = {}


_abbr_exc = [
    {ORTH: "м", LEMMA: "метар", NORM: "метар"},
    {ORTH: "мм", LEMMA: "милиметар", NORM: "милиметар"},
    {ORTH: "цм", LEMMA: "центиметар", NORM: "центиметар"},
    {ORTH: "см", LEMMA: "сантиметар", NORM: "сантиметар"},
    {ORTH: "дм", LEMMA: "дециметар", NORM: "дециметар"},
    {ORTH: "км", LEMMA: "километар", NORM: "километар"},
    {ORTH: "кг", LEMMA: "килограм", NORM: "килограм"},
    {ORTH: "дкг", LEMMA: "декаграм", NORM: "декаграм"},
    {ORTH: "дг", LEMMA: "дециграм", NORM: "дециграм"},
    {ORTH: "мг", LEMMA: "милиграм", NORM: "милиграм"},
    {ORTH: "г", LEMMA: "грам", NORM: "грам"},
    {ORTH: "т", LEMMA: "тон", NORM: "тон"},
    {ORTH: "кл", LEMMA: "килолитар", NORM: "килолитар"},
    {ORTH: "хл", LEMMA: "хектолитар", NORM: "хектолитар"},
    {ORTH: "дкл", LEMMA: "декалитар", NORM: "декалитар"},
    {ORTH: "л", LEMMA: "литар", NORM: "литар"},
    {ORTH: "дл", LEMMA: "децилитар", NORM: "децилитар"}

]
for abbr in _abbr_exc:
    _exc[abbr[ORTH]] = [abbr]

_abbr_line_exc = [
    {ORTH: "д-р", LEMMA: "доктор", NORM: "доктор"},
    {ORTH: "м-р", LEMMA: "магистер", NORM: "магистер"},
    {ORTH: "г-ѓа", LEMMA: "госпоѓа", NORM: "госпоѓа"},
    {ORTH: "г-ца", LEMMA: "госпоѓица", NORM: "госпоѓица"},
    {ORTH: "г-дин", LEMMA: "господин", NORM: "господин"},

]

for abbr in _abbr_line_exc:
    _exc[abbr[ORTH]] = [abbr]

_abbr_dot_exc = [
    {ORTH: "в.", LEMMA: "век", NORM: "век"},
    {ORTH: "в.д.", LEMMA: "вршител на должност", NORM: "вршител на должност"},
    {ORTH: "г.", LEMMA: "година", NORM: "година"},
    {ORTH: "г.г.", LEMMA: "господин господин", NORM: "господин господин"},
    {ORTH: "м.р.", LEMMA: "машки род", NORM: "машки род"},
    {ORTH: "год.", LEMMA: "женски род", NORM: "женски род"},
    {ORTH: "с.р.", LEMMA: "среден род", NORM: "среден род"},
    {ORTH: "н.е.", LEMMA: "наша ера", NORM: "наша ера"},
    {ORTH: "о.г.", LEMMA: "оваа година", NORM: "оваа година"},
    {ORTH: "о.м.", LEMMA: "овој месец", NORM: "овој месец"},
    {ORTH: "с.", LEMMA: "село", NORM: "село"},
    {ORTH: "т.", LEMMA: "точка", NORM: "точка"},
    {ORTH: "т.е.", LEMMA: "то ест", NORM: "то ест"},
    {ORTH: "т.н.", LEMMA: "таканаречен", NORM: "таканаречен"},

    {ORTH: "бр.", LEMMA: "број", NORM: "број"},
    {ORTH: "гр.", LEMMA: "град", NORM: "град"},
    {ORTH: "др.", LEMMA: "другар", NORM: "другар"},
    {ORTH: "и др.", LEMMA: "и друго", NORM: "и друго"},
    {ORTH: "и сл.", LEMMA: "и слично", NORM: "и слично"},
    {ORTH: "кн.", LEMMA: "книга", NORM: "книга"},
    {ORTH: "мн.", LEMMA: "множина", NORM: "множина"},
    {ORTH: "на пр.", LEMMA: "на пример", NORM: "на пример"},
    {ORTH: "св.", LEMMA: "свети", NORM: "свети"},
    {ORTH: "сп.", LEMMA: "списание", NORM: "списание"},
    {ORTH: "с.", LEMMA: "страница", NORM: "страница"},
    {ORTH: "стр.", LEMMA: "страница", NORM: "страница"},
    {ORTH: "чл.", LEMMA: "член", NORM: "член"},

    {ORTH: "арх.", LEMMA: "архитект", NORM: "архитект"},
    {ORTH: "бел.", LEMMA: "белешка", NORM: "белешка"},
    {ORTH: "гимн.", LEMMA: "гимназија", NORM: "гимназија"},
    {ORTH: "ден.", LEMMA: "денар", NORM: "денар"},
    {ORTH: "ул.", LEMMA: "улица", NORM: "улица"},
    {ORTH: "инж.", LEMMA: "инженер", NORM: "инженер"},
    {ORTH: "проф.", LEMMA: "професор", NORM: "професор"},
    {ORTH: "студ.", LEMMA: "студент", NORM: "студент"},
    {ORTH: "бот.", LEMMA: "ботаника", NORM: "ботаника"},
    {ORTH: "мат.", LEMMA: "математика", NORM: "математика"},
    {ORTH: "мед.", LEMMA: "медицина", NORM: "медицина"},
    {ORTH: "прил.", LEMMA: "прилог", NORM: "прилог"},
    {ORTH: "прид.", LEMMA: "придавка", NORM: "придавка"},
    {ORTH: "сврз.", LEMMA: "сврзник", NORM: "сврзник"},
    {ORTH: "физ.", LEMMA: "физика", NORM: "физика"},
    {ORTH: "хем.", LEMMA: "хемија", NORM: "хемија"},
    {ORTH: "пр. н.", LEMMA: "природни науки", NORM: "природни науки"},
    {ORTH: "истор.", LEMMA: "историја", NORM: "историја"},
    {ORTH: "геогр.", LEMMA: "географија", NORM: "географија"},
    {ORTH: "литер.", LEMMA: "литература", NORM: "литература"},


]

for abbr in _abbr_dot_exc:
    _exc[abbr[ORTH]] = [abbr]


TOKENIZER_EXCEPTIONS = _exc
