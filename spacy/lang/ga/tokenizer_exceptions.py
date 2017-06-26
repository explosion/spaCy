# encoding: utf8
from __future__ import unicode_literals

from ..symbols import ORTH, LEMMA, NORM, POS


_exc = {
    "'acha'n": [
        {ORTH: "'ach", LEMMA: "gach", NORM: "gach", POS: DET},
        {ORTH: "a'n", LEMMA: "aon", NORM: "aon", POS: DET}],

    "dem'": [
        {ORTH: "de", LEMMA: "de", NORM: "de", POS: ADP},
        {ORTH: "m'", LEMMA: "mo", NORM: "mo", POS: DET}],

    "ded'": [
        {ORTH: "de", LEMMA: "de", NORM: "de", POS: ADP},
        {ORTH: "d'", LEMMA: "do", NORM: "do", POS: DET}],

    "lem'": [
        {ORTH: "le", LEMMA: "le", NORM: "le", POS: ADP},
        {ORTH: "m'", LEMMA: "mo", NORM: "mo", POS: DET}],

    "led'": [
        {ORTH: "le", LEMMA: "le", NORM: "le", POS: ADP},
        {ORTH: "d'", LEMMA: "mo", NORM: "do", POS: DET}],

    "a.C.n.": [
        {ORTH: "a.", LEMMA: "ante", POS: X},
        {ORTH: "C.", LEMMA: "Christum", POS: X},
        {ORTH: "n.", LEMMA: "natum", POS: X}],

    "m.sh.": [
        {ORTH: "m.", LEMMA: "mar", POS: ADP},
        {ORTH: "sh.", LEMMA: "sampla", POS: NOUN}],

    "M.F.": [
        {ORTH: "M.", LEMMA: "Meán", POS: NOUN},
        {ORTH: "F.", LEMMA: "Fómhar", POS: NOUN}],

    "M.Fómh.": [
        {ORTH: "M.", LEMMA: "Meán", POS: NOUN},
        {ORTH: "Fómh.", LEMMA: "Fómhar", POS: NOUN}],

    "R.C.": [
        {ORTH: "R.", LEMMA: "roimh", POS: ADP},
        {ORTH: "C.", LEMMA: "Críost", POS: NOUN}],

    "r.Ch.": [
        {ORTH: "r.", LEMMA: "roimh", POS: ADP},
        {ORTH: "Ch.", LEMMA: "Críost", POS: NOUN}],

    "r.Chr.": [
        {ORTH: "r.", LEMMA: "roimh", POS: ADP},
        {ORTH: "Chr.", LEMMA: "Críost", POS: NOUN}],

    "R.Ch.": [
        {ORTH: "R.", LEMMA: "roimh", POS: ADP},
        {ORTH: "Ch.", LEMMA: "Críost", POS: NOUN}],

    "R.Chr.": [
        {ORTH: "R.", LEMMA: "roimh", POS: ADP},
        {ORTH: "Chr.", LEMMA: "Críost", POS: NOUN}],

    "⁊rl.": [
        {ORTH: "⁊", LEMMA: "agus", POS: CCONJ},
        {ORTH: "rl.", LEMMA: "araile", POS: ADJ}],

    "srl.": [
        {ORTH: "s", LEMMA: "agus", POS: CCONJ},
        {ORTH: "rl.", LEMMA: "araile", POS: ADJ}],

}

for exc_data in [
    {ORTH: "'gus", LEMMA: "agus", NORM: "agus", POS: CCONJ},
    {ORTH: "'ach", LEMMA: "gach", NORM: "gach", POS: DET},
    {ORTH: "ao'", LEMMA: "aon", NORM: "aon"},
    {ORTH: "'niar", LEMMA: "aniar", NORM: "aniar", POS: ADV},
    {ORTH: "'níos", LEMMA: "aníos", NORM: "aníos", POS: ADV},
    {ORTH: "'ndiu", LEMMA: "inniu", NORM: "inniu", POS: ADV},
    {ORTH: "'nocht", LEMMA: "anocht", NORM: "anocht", POS: ADV},
    {ORTH: "m'", LEMMA: "mo", POS: DET},
    {ORTH: "Aib.", LEMMA: "Aibreán", POS: NOUN},
    {ORTH: "Ath.", LEMMA: "athair", POS: NOUN},
    {ORTH: "Beal.", LEMMA: "Bealtaine", POS: NOUN},
    {ORTH: "Co.", LEMMA: "contae", POS: NOUN},
    {ORTH: "Ean.", LEMMA: "Eanáir", POS: NOUN},
    {ORTH: "Feab.", LEMMA: "Feabhra", POS: NOUN},
    {ORTH: "gCo.", LEMMA: "contae", POS: NOUN},
    {ORTH: ".i.", LEMMA: "eadhon", POS: ADV},
    {ORTH: "lch.", LEMMA: "leathanach", POS: NOUN},
    {ORTH: "Lch.", LEMMA: "leathanach", POS: NOUN},
    {ORTH: "lgh.", LEMMA: "leathanach", POS: NOUN},
    {ORTH: "Lgh.", LEMMA: "leathanach", POS: NOUN},
    {ORTH: "Lún.", LEMMA: "Lúnasa", POS: NOUN},
    {ORTH: "Már.", LEMMA: "Márta", POS: NOUN},
    {ORTH: "Meith.", LEMMA: "Meitheamh", POS: NOUN},
    {ORTH: "Noll.", LEMMA: "Nollaig", POS: NOUN},
    {ORTH: "Samh.", LEMMA: "Samhain", POS: NOUN},
    {ORTH: "tAth.", LEMMA: "athair", POS: NOUN},
    {ORTH: "tUas.", LEMMA: "Uasal", POS: NOUN},
    {ORTH: "teo.", LEMMA: "teoranta", POS: NOUN},
    {ORTH: "Teo.", LEMMA: "teoranta", POS: NOUN},
    {ORTH: "Uas.", LEMMA: "Uasal", POS: NOUN},
    {ORTH: "uimh.", LEMMA: "uimhir", POS: NOUN},
    {ORTH: "Uimh.", LEMMA: "uimhir", POS: NOUN}]:
    _exc[exc_data[ORTH]] = [dict(exc_data)],

for orth in [
    "d'"]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = dict(_exc)
