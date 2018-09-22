# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM, PRON_LEMMA


_exc = {
    "às": [
        {ORTH: "à", NORM: "a"},
        {ORTH: "s", NORM: "as"}],

    "ao": [
        {ORTH: "a"},
        {ORTH: "o"}],

    "aos": [
        {ORTH: "a"},
        {ORTH: "os"}],

    "àquele": [
        {ORTH: "à", NORM: "a"},
        {ORTH: "quele", NORM: "aquele"}],

    "àquela": [
        {ORTH: "à", NORM: "a"},
        {ORTH: "quela", NORM: "aquela"}],

    "àqueles": [
        {ORTH: "à", NORM: "a"},
        {ORTH: "queles", NORM: "aqueles"}],

    "àquelas": [
        {ORTH: "à", NORM: "a"},
        {ORTH: "quelas", NORM: "aquelas"}],

    "àquilo": [
        {ORTH: "à", NORM: "a"},
        {ORTH: "quilo", NORM: "aquilo"}],

    "aonde": [
        {ORTH: "a"},
        {ORTH: "onde"}]
}


# Contractions

_per_pron = ["ele", "ela", "eles", "elas"]
_dem_pron = ["este", "esta", "estes", "estas", "isto", "esse", "essa", "esses",
             "essas", "isso", "aquele", "aquela", "aqueles", "aquelas", "aquilo"]
_und_pron = ["outro", "outra", "outros", "outras"]
_adv = ["aqui", "aí", "ali", "além"]


for orth in _per_pron + _dem_pron + _und_pron + _adv:
    _exc["d" + orth] = [
        {ORTH: "d", NORM: "de"},
        {ORTH: orth}]

for orth in _per_pron + _dem_pron + _und_pron:
    _exc["n" + orth] = [
        {ORTH: "n", NORM: "em"},
        {ORTH: orth}]



for orth in [
    "Adm.", "Dr.", "e.g.", "E.g.", "E.G.", "Gen.", "Gov.", "i.e.", "I.e.",
    "I.E.", "Jr.", "Ltd.", "p.m.", "Ph.D.", "Rep.", "Rev.", "Sen.", "Sr.",
    "Sra.", "vs.", "tel.", "pág.", "pag."]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
