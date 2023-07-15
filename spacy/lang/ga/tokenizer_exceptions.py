from ...symbols import NORM, ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

_exc = {
    "'acha'n": [{ORTH: "'ach", NORM: "gach"}, {ORTH: "a'n", NORM: "aon"}],
    "dem'": [{ORTH: "de", NORM: "de"}, {ORTH: "m'", NORM: "mo"}],
    "ded'": [{ORTH: "de", NORM: "de"}, {ORTH: "d'", NORM: "do"}],
    "lem'": [{ORTH: "le", NORM: "le"}, {ORTH: "m'", NORM: "mo"}],
    "led'": [{ORTH: "le", NORM: "le"}, {ORTH: "d'", NORM: "do"}],
    "théis": [{ORTH: "th", NORM: "tar"}, {ORTH: "éis", NORM: "éis"}],
    "tréis": [{ORTH: "tr", NORM: "tar"}, {ORTH: "éis", NORM: "éis"}],
}

for exc_data in [
    {ORTH: "'gus", NORM: "agus"},
    {ORTH: "'ach", NORM: "gach"},
    {ORTH: "ao'", NORM: "aon"},
    {ORTH: "'niar", NORM: "aniar"},
    {ORTH: "'níos", NORM: "aníos"},
    {ORTH: "'ndiu", NORM: "inniu"},
    {ORTH: "'nocht", NORM: "anocht"},
    {ORTH: "m'"},
    {ORTH: "Aib."},
    {ORTH: "Ath."},
    {ORTH: "Beal."},
    {ORTH: "a.C.n."},
    {ORTH: "m.sh."},
    {ORTH: "M.F."},
    {ORTH: "M.Fómh."},
    {ORTH: "D.F."},
    {ORTH: "D.Fómh."},
    {ORTH: "r.C."},
    {ORTH: "R.C."},
    {ORTH: "r.Ch."},
    {ORTH: "r.Chr."},
    {ORTH: "R.Ch."},
    {ORTH: "R.Chr."},
    {ORTH: "⁊rl."},
    {ORTH: "srl."},
    {ORTH: "Co."},
    {ORTH: "Ean."},
    {ORTH: "Feab."},
    {ORTH: "gCo."},
    {ORTH: ".i."},
    {ORTH: "B'"},
    {ORTH: "b'"},
    {ORTH: "lch."},
    {ORTH: "Lch."},
    {ORTH: "lgh."},
    {ORTH: "Lgh."},
    {ORTH: "Lún."},
    {ORTH: "Már."},
    {ORTH: "Meith."},
    {ORTH: "Noll."},
    {ORTH: "Samh."},
    {ORTH: "tAth."},
    {ORTH: "tUas."},
    {ORTH: "teo."},
    {ORTH: "Teo."},
    {ORTH: "Uas."},
    {ORTH: "uimh."},
    {ORTH: "Uimh."},
]:
    _exc[exc_data[ORTH]] = [exc_data]

for orth in ["d'", "D'"]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
