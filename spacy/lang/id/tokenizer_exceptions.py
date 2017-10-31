# coding: utf8
from __future__ import unicode_literals

import regex as re

from ._tokenizer_exceptions_list import ID_BASE_EXCEPTIONS
from ..tokenizer_exceptions import URL_PATTERN
from ...symbols import ORTH


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


for orth in [
    "'d", "a.m.", "Adm.", "Bros.", "co.", "Co.", "Corp.", "D.C.", "Dr.", "e.g.",
    "E.g.", "E.G.", "Gen.", "Gov.", "i.e.", "I.e.", "I.E.", "Inc.", "Jr.",
    "Ltd.", "Md.", "Messrs.", "Mo.", "Mont.", "Mr.", "Mrs.", "Ms.", "p.m.",
    "Ph.D.", "Rep.", "Rev.", "Sen.", "St.", "vs.",
    "B.A.", "B.Ch.E.", "B.Sc.", "Dr.", "Dra.", "Drs.", "Hj.", "Ka.", "Kp.",
    "M.Ag.", "M.Hum.", "M.Kes,", "M.Kom.", "M.M.", "M.P.", "M.Pd.", "M.Sc.",
    "M.Si.", "M.Sn.", "M.T.", "M.Th.", "No.", "Pjs.", "Plt.", "R.A.", "S.Ag.",
    "S.E.", "S.H.", "S.Hut.", "S.K.M.", "S.Kedg.", "S.Kedh.", "S.Kom.",
    "S.Pd.", "S.Pol.", "S.Psi.", "S.S.", "S.Sos.", "S.T.", "S.Tekp.", "S.Th.",
    "a.l.", "a.n.", "a.s.", "b.d.", "d.a.", "d.l.", "d/h", "dkk.", "dll.",
    "dr.", "drh.", "ds.", "dsb.", "dst.", "faks.", "fax.", "hlm.", "i/o",
    "n.b.", "p.p." "pjs.", "s.d.", "tel.", "u.p.",
    ]:
    _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = _exc
