from ...symbols import ORTH, NORM


_exc = {}


_abbr_exc = [
    {ORTH: "м", NORM: "метър"},
    {ORTH: "мм", NORM: "милиметър"},
    {ORTH: "см", NORM: "сантиметър"},
    {ORTH: "дм", NORM: "дециметър"},
    {ORTH: "км", NORM: "километър"},
    {ORTH: "кг", NORM: "килограм"},
    {ORTH: "мг", NORM: "милиграм"},
    {ORTH: "г", NORM: "грам"},
    {ORTH: "т", NORM: "тон"},
    {ORTH: "хл", NORM: "хектолиър"},
    {ORTH: "дкл", NORM: "декалитър"},
    {ORTH: "л", NORM: "литър"},
]
for abbr in _abbr_exc:
    _exc[abbr[ORTH]] = [abbr]

_abbr_line_exc = [
    {ORTH: "г-жа", NORM: "госпожа"},
    {ORTH: "г-н", NORM: "господин"},
    {ORTH: "г-ца", NORM: "госпожица"},
    {ORTH: "д-р", NORM: "доктор"},
    {ORTH: "о-в", NORM: "остров"},
    {ORTH: "п-в", NORM: "полуостров"},
]

for abbr in _abbr_line_exc:
    _exc[abbr[ORTH]] = [abbr]

_abbr_dot_exc = [
    {ORTH: "акад.", NORM: "академик"},
    {ORTH: "ал.", NORM: "алинея"},
    {ORTH: "арх.", NORM: "архитект"},
    {ORTH: "бл.", NORM: "блок"},
    {ORTH: "бр.", NORM: "брой"},
    {ORTH: "бул.", NORM: "булевард"},
    {ORTH: "в.", NORM: "век"},
    {ORTH: "г.", NORM: "година"},
    {ORTH: "гр.", NORM: "град"},
    {ORTH: "ж.р.", NORM: "женски род"},
    {ORTH: "инж.", NORM: "инженер"},
    {ORTH: "лв.", NORM: "лев"},
    {ORTH: "м.р.", NORM: "мъжки род"},
    {ORTH: "мат.", NORM: "математика"},
    {ORTH: "мед.", NORM: "медицина"},
    {ORTH: "пл.", NORM: "площад"},
    {ORTH: "проф.", NORM: "професор"},
    {ORTH: "с.", NORM: "село"},
    {ORTH: "с.р.", NORM: "среден род"},
    {ORTH: "св.", NORM: "свети"},
    {ORTH: "сп.", NORM: "списание"},
    {ORTH: "стр.", NORM: "страница"},
    {ORTH: "ул.", NORM: "улица"},
    {ORTH: "чл.", NORM: "член"},
]

for abbr in _abbr_dot_exc:
    _exc[abbr[ORTH]] = [abbr]


TOKENIZER_EXCEPTIONS = _exc
