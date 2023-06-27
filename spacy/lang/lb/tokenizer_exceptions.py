from ...symbols import NORM, ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

# TODO
# treat other apostrophes within words as part of the word: [op d'mannst], [fir d'éischt] (= exceptions)

_exc = {}

# translate / delete what is not necessary
for exc_data in [
    {ORTH: "’t", NORM: "et"},
    {ORTH: "’T", NORM: "et"},
    {ORTH: "'t", NORM: "et"},
    {ORTH: "'T", NORM: "et"},
    {ORTH: "wgl.", NORM: "wannechgelift"},
    {ORTH: "M.", NORM: "Monsieur"},
    {ORTH: "Mme.", NORM: "Madame"},
    {ORTH: "Dr.", NORM: "Dokter"},
    {ORTH: "Tel.", NORM: "Telefon"},
    {ORTH: "asw.", NORM: "an sou weider"},
    {ORTH: "etc.", NORM: "et cetera"},
    {ORTH: "bzw.", NORM: "bezéiungsweis"},
    {ORTH: "Jan.", NORM: "Januar"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


# to be extended
for orth in [
    "z.B.",
    "Dipl.",
    "Dr.",
    "etc.",
    "i.e.",
    "o.k.",
    "O.K.",
    "p.a.",
    "p.s.",
    "P.S.",
    "phil.",
    "q.e.d.",
    "R.I.P.",
    "rer.",
    "sen.",
    "ë.a.",
    "U.S.",
    "U.S.A.",
]:
    _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
