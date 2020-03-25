# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH


_exc = {}


for orth in [
    "Adm.",
    "Art.",
    "art.",
    "Av.",
    "av.",
    "Cia.",
    "dom.",
    "Dr.",
    "dr.",
    "e.g.",
    "E.g.",
    "E.G.",
    "e/ou",
    "ed.",
    "eng.",
    "etc.",
    "Fund.",
    "Gen.",
    "Gov.",
    "i.e.",
    "I.e.",
    "I.E.",
    "Inc.",
    "Jr.",
    "km/h",
    "Ltd.",
    "Mr.",
    "p.m.",
    "Ph.D.",
    "Rep.",
    "Rev.",
    "S/A",
    "Sen.",
    "Sr.",
    "sr.",
    "Sra.",
    "sra.",
    "vs.",
    "tel.",
    "pág.",
    "pag.",
]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
