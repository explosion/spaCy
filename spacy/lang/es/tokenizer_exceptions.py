# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, TAG, NORM, ADP, DET
from ...deprecated import PRON_LEMMA


_exc = {
    "al": [
        {ORTH: "a", LEMMA: "a", TAG: ADP},
        {ORTH: "l", LEMMA: "el", TAG: DET}],

    "consigo": [
        {ORTH: "con", LEMMA: "con"},
        {ORTH: "sigo", LEMMA: PRON_LEMMA, NORM: "sí"}],

    "conmigo": [
        {ORTH: "con", LEMMA: "con"},
        {ORTH: "migo", LEMMA: PRON_LEMMA, NORM: "mí"}],

    "contigo": [
        {ORTH: "con", LEMMA: "con"},
        {ORTH: "tigo", LEMMA: PRON_LEMMA, NORM: "ti"}],

    "del": [
        {ORTH: "de", LEMMA: "de", TAG: ADP},
        {ORTH: "l", LEMMA: "el", TAG: DET}],

    "pel": [
        {ORTH: "pe", LEMMA: "per", TAG: ADP},
        {ORTH: "l", LEMMA: "el", TAG: DET}],

    "pal": [
        {ORTH: "pa", LEMMA: "para"},
        {ORTH: "l", LEMMA: "el"}],

    "pala": [
        {ORTH: "pa", LEMMA: "para"},
        {ORTH: "la"}]
}


for exc_data in [
    {ORTH: "aprox.", LEMMA: "aproximadamente"},
    {ORTH: "dna.", LEMMA: "docena"},
    {ORTH: "esq.", LEMMA: "esquina"},
    {ORTH: "pág.", LEMMA: "página"},
    {ORTH: "p.ej.", LEMMA: "por ejemplo"},
    {ORTH: "Ud.", LEMMA: PRON_LEMMA, NORM: "usted"},
    {ORTH: "Vd.", LEMMA: PRON_LEMMA, NORM: "usted"},
    {ORTH: "Uds.", LEMMA: PRON_LEMMA, NORM: "ustedes"},
    {ORTH: "Vds.", LEMMA: PRON_LEMMA, NORM: "ustedes"}]:
    _exc[exc_data[ORTH]] = [dict(exc_data)]


# Times

_exc["12m."] = [
    {ORTH: "12"},
    {ORTH: "m.", LEMMA: "p.m."}]


for h in range(1, 12 + 1):
    for period in ["a.m.", "am"]:
        _exc["%d%s" % (h, period)] = [
            {ORTH: "%d" % h},
            {ORTH: period, LEMMA: "a.m."}]
    for period in ["p.m.", "pm"]:
        _exc["%d%s" % (h, period)] = [
            {ORTH: "%d" % h},
            {ORTH: period, LEMMA: "p.m."}]


for orth in [
    "a.C.", "a.J.C.", "apdo.", "Av.", "Avda.", "Cía.", "etc.", "Gob.", "Gral.",
    "Ing.", "J.C.", "Lic.", "m.n.", "no.", "núm.", "P.D.", "Prof.", "Profa.",
    "q.e.p.d.", "S.A.", "S.L.", "s.s.s.", "Sr.", "Sra.", "Srta."]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = dict(_exc)
