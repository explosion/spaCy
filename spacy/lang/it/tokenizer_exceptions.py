from ...symbols import ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

_exc = {
    "all'art.": [{ORTH: "all'"}, {ORTH: "art."}],
    "dall'art.": [{ORTH: "dall'"}, {ORTH: "art."}],
    "dell'art.": [{ORTH: "dell'"}, {ORTH: "art."}],
    "L'art.": [{ORTH: "L'"}, {ORTH: "art."}],
    "l'art.": [{ORTH: "l'"}, {ORTH: "art."}],
    "nell'art.": [{ORTH: "nell'"}, {ORTH: "art."}],
    "po'": [{ORTH: "po'"}],
    "sett..": [{ORTH: "sett."}, {ORTH: "."}],
}

for orth in [
    "..",
    "....",
    "a.C.",
    "al.",
    "all-path",
    "art.",
    "Art.",
    "artt.",
    "att.",
    "avv.",
    "Avv.",
    "by-pass",
    "c.d.",
    "c/c",
    "C.so",
    "centro-sinistra",
    "check-up",
    "Civ.",
    "cm.",
    "Cod.",
    "col.",
    "Cost.",
    "d.C.",
    'de"',
    "distr.",
    "E'",
    "ecc.",
    "e-mail",
    "e/o",
    "etc.",
    "Jr.",
    "n°",
    "nord-est",
    "pag.",
    "Proc.",
    "prof.",
    "sett.",
    "s.p.a.",
    "s.n.c",
    "s.r.l",
    "ss.",
    "St.",
    "tel.",
    "week-end",
]:
    _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
