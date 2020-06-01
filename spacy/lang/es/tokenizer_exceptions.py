# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM, PRON_LEMMA


_exc = {}


for exc_data in [
    {ORTH: "n°", LEMMA: "número"},
    {ORTH: "°C", LEMMA: "grados Celcius"},
    {ORTH: "aprox.", LEMMA: "aproximadamente"},
    {ORTH: "dna.", LEMMA: "docena"},
    {ORTH: "dpto.", LEMMA: "departamento"},
    {ORTH: "ej.", LEMMA: "ejemplo"},
    {ORTH: "esq.", LEMMA: "esquina"},
    {ORTH: "pág.", LEMMA: "página"},
    {ORTH: "p.ej.", LEMMA: "por ejemplo"},
    {ORTH: "Ud.", LEMMA: PRON_LEMMA, NORM: "usted"},
    {ORTH: "Vd.", LEMMA: PRON_LEMMA, NORM: "usted"},
    {ORTH: "Uds.", LEMMA: PRON_LEMMA, NORM: "ustedes"},
    {ORTH: "Vds.", LEMMA: PRON_LEMMA, NORM: "ustedes"},
    {ORTH: "vol.", NORM: "volúmen"},

]:
    _exc[exc_data[ORTH]] = [exc_data]


# Times

_exc["12m."] = [{ORTH: "12"}, {ORTH: "m.", LEMMA: "p.m."}]


for h in range(1, 12 + 1):
    for period in ["a.m.", "am"]:
        _exc["%d%s" % (h, period)] = [{ORTH: "%d" % h}, {ORTH: period, LEMMA: "a.m."}]
    for period in ["p.m.", "pm"]:
        _exc["%d%s" % (h, period)] = [{ORTH: "%d" % h}, {ORTH: period, LEMMA: "p.m."}]


for orth in [
    "a.C.",
    "a.J.C.",
    "d.C.",
    "d.J.C.",
    "apdo.",
    "Av.",
    "Avda.",
    "Cía.",
    "Dr.",
    "Dra.",
    "EE.UU.",
    "etc.",
    "fig.",
    "Gob.",
    "Gral.",
    "Ing.",
    "J.C.",
    "km/h",
    "Lic.",
    "m.n.",
    "núm.",
    "P.D.",
    "Prof.",
    "Profa.",
    "q.e.p.d.",
    "Q.E.P.D."
    "S.A.",
    "S.L.",
    "S.R.L."
    "s.s.s.",
    "Sr.",
    "Sra.",
    "Srta.",
]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
