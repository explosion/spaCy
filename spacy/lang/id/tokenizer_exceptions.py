# coding: utf8
from __future__ import unicode_literals

import regex as re

from ._tokenizer_exceptions_list import ID_BASE_EXCEPTIONS
from ..tokenizer_exceptions import URL_PATTERN
from ...symbols import ORTH, LEMMA, NORM


_exc = {}

for orth in ID_BASE_EXCEPTIONS:
    _exc[orth] = [{ORTH: orth}]

    orth_title = orth.title()
    _exc[orth_title] = [{ORTH: orth_title}]

    orth_caps = orth.upper()
    _exc[orth_caps] = [{ORTH: orth_caps}]

    orth_lower = orth.lower()
    _exc[orth_lower] = [{ORTH: orth_lower}]

    if '-' in orth:
        orth_title = '-'.join([part.title() for part in orth.split('-')])
        _exc[orth_title] = [{ORTH: orth_title}]

        orth_caps = '-'.join([part.upper() for part in orth.split('-')])
        _exc[orth_caps] = [{ORTH: orth_caps}]

for exc_data in [
    {ORTH: "CKG", LEMMA: "Cakung", NORM: "Cakung"},
    {ORTH: "CGP", LEMMA: "Grogol Petamburan", NORM: "Grogol Petamburan"},
    {ORTH: "KSU", LEMMA: "Kepulauan Seribu Utara", NORM: "Kepulauan Seribu Utara"},
    {ORTH: "KYB", LEMMA: "Kebayoran Baru", NORM: "Kebayoran Baru"},
    {ORTH: "TJP", LEMMA: "Tanjungpriok", NORM: "Tanjungpriok"},
    {ORTH: "TNA", LEMMA: "Tanah Abang", NORM: "Tanah Abang"},

    {ORTH: "BEK", LEMMA: "Bengkayang", NORM: "Bengkayang"},
    {ORTH: "KTP", LEMMA: "Ketapang", NORM: "Ketapang"},
    {ORTH: "MPW", LEMMA: "Mempawah", NORM: "Mempawah"},
    {ORTH: "NGP", LEMMA: "Nanga Pinoh", NORM: "Nanga Pinoh"},
    {ORTH: "NBA", LEMMA: "Ngabang", NORM: "Ngabang"},
    {ORTH: "PTK", LEMMA: "Pontianak", NORM: "Pontianak"},
    {ORTH: "PTS", LEMMA: "Putussibau", NORM: "Putussibau"},
    {ORTH: "SBS", LEMMA: "Sambas", NORM: "Sambas"},
    {ORTH: "SAG", LEMMA: "Sanggau", NORM: "Sanggau"},
    {ORTH: "SED", LEMMA: "Sekadau", NORM: "Sekadau"},
    {ORTH: "SKW", LEMMA: "Singkawang", NORM: "Singkawang"},
    {ORTH: "STG", LEMMA: "Sintang", NORM: "Sintang"},
    {ORTH: "SKD", LEMMA: "Sukadane", NORM: "Sukadane"},
    {ORTH: "SRY", LEMMA: "Sungai Raya", NORM: "Sungai Raya"},

    {ORTH: "Jan.", LEMMA: "Januari", NORM: "Januari"},
    {ORTH: "Feb.", LEMMA: "Februari", NORM: "Februari"},
    {ORTH: "Mar.", LEMMA: "Maret", NORM: "Maret"},
    {ORTH: "Apr.", LEMMA: "April", NORM: "April"},
    {ORTH: "Jun.", LEMMA: "Juni", NORM: "Juni"},
    {ORTH: "Jul.", LEMMA: "Juli", NORM: "Juli"},
    {ORTH: "Agu.", LEMMA: "Agustus", NORM: "Agustus"},
    {ORTH: "Ags.", LEMMA: "Agustus", NORM: "Agustus"},
    {ORTH: "Sep.", LEMMA: "September", NORM: "September"},
    {ORTH: "Okt.", LEMMA: "Oktober", NORM: "Oktober"},
    {ORTH: "Nov.", LEMMA: "November", NORM: "November"},
    {ORTH: "Des.", LEMMA: "Desember", NORM: "Desember"}]:
    _exc[exc_data[ORTH]] = [exc_data]

for orth in [
    "A.AB.", "A.Ma.", "A.Md.", "A.Md.Keb.", "A.Md.Kep.", "A.P.",
    "B.A.", "B.Ch.E.", "B.Sc.", "Dr.", "Dra.", "Drs.", "Hj.", "Ka.", "Kp.",
    "M.AB", "M.Ag.", "M.AP", "M.Arl", "M.A.R.S", "M.Hum.", "M.I.Kom.", "M.Kes,",
    "M.Kom.", "M.M.", "M.P.", "M.Pd.", "M.Psi.", "M.Psi.T.", "M.Sc.", "M.SArl",
    "M.Si.", "M.Sn.", "M.T.", "M.Th.", "No.", "Pjs.", "Plt.", "R.A.",
    "S.AB", "S.AP", "S.Adm", "S.Ag.", "S.Agr", "S.Ant", "S.Arl", "S.Ars",
    "S.A.R.S", "S.Ds", "S.E.", "S.E.I.", "S.Farm", "S.Gz.", "S.H.", "S.Han",
    "S.H.Int", "S.Hum", "S.Hut.", "S.In.", "S.IK.", "S.I.Kom.", "S.I.P", "S.IP",
    "S.P.", "S.Pt", "S.Psi", "S.Ptk", "S.Keb", "S.Ked", "S.Kep", "S.KG", "S.KH",
    "S.Kel", "S.K.M.", "S.Kedg.", "S.Kedh.", "S.Kom.", "S.KPM", "S.Mb", "S.Mat",
    "S.Par", "S.Pd.", "S.Pd.I.", "S.Pd.SD", "S.Pol.", "S.Psi.", "S.S.", "S.SArl.",
    "S.Sn", "S.Si.", "S.Si.Teol.", "S.SI.", "S.ST.", "S.ST.Han", "S.STP", "S.Sos.",
    "S.Sy.", "S.T.", "S.T.Han", "S.Th.", "S.Th.I" "S.TI.", "S.T.P.", "S.TrK",
    "S.Tekp.", "S.Th.",
    "a.l.", "a.n.", "a.s.", "b.d.", "d.a.", "d.l.", "d/h", "dkk.", "dll.",
    "dr.", "drh.", "ds.", "dsb.", "dst.", "faks.", "fax.", "hlm.", "i/o",
    "n.b.", "p.p." "pjs.", "s.d.", "tel.", "u.p.",
    ]:
    _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = _exc
