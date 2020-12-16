# coding: utf8
from __future__ import unicode_literals
from ...symbols import ORTH, LEMMA

_exc = {
    "all'art.": [{ORTH: "all'"}, {ORTH: "art."}],
    "dall'art.": [{ORTH: "dall'"}, {ORTH: "art."}],
    "dell'art.": [{ORTH: "dell'"}, {ORTH: "art."}],
    "L'art.": [{ORTH: "L'"}, {ORTH: "art."}],
    "l'art.": [{ORTH: "l'"}, {ORTH: "art."}],
    "nell'art.": [{ORTH: "nell'"}, {ORTH: "art."}],
    "po'": [{ORTH: "po'", LEMMA: "poco"}],
    "sett..": [{ORTH: "sett."}, {ORTH: "."}],
}

for orth in [
    "..",
    "....",
    "al.",
    "all-path",
    "art.",
    "Art.",
    "artt.",
    "att.",
    "by-pass",
    "c.d.",
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
    "ss.",
    "St.",
    "tel.",
    "week-end",
]:
    _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = _exc
