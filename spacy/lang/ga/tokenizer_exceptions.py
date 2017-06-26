# encoding: utf8
from __future__ import unicode_literals

from ..symbols import ORTH, LEMMA, NORM


_exc = {
    "'acha'n": [
        {ORTH: "'ach", LEMMA: "gach", NORM: "gach"},
        {ORTH: "a'n", LEMMA: "aon", NORM: "aon"}],

    "dem'": [
        {ORTH: "de", LEMMA: "de", NORM: "de"},
        {ORTH: "m'", LEMMA: "mo", NORM: "mo"}],

    "ded'": [
        {ORTH: "de", LEMMA: "de", NORM: "de"},
        {ORTH: "d'", LEMMA: "do", NORM: "do"}],

    "lem'": [
        {ORTH: "le", LEMMA: "le", NORM: "le"},
        {ORTH: "m'", LEMMA: "mo", NORM: "mo"}],

    "led'": [
        {ORTH: "le", LEMMA: "le", NORM: "le"},
        {ORTH: "d'", LEMMA: "mo", NORM: "do"}],

    "a.C.n.": [
        {ORTH: "a.", LEMMA: "ante"},
        {ORTH: "C.", LEMMA: "Christum"},
        {ORTH: "n.", LEMMA: "natum"}],

    "m.sh.": [
        {ORTH: "m.", LEMMA: "mar"},
        {ORTH: "sh.", LEMMA: "sampla"}],

    "M.F.": [
        {ORTH: "M.", LEMMA: "Meán"},
        {ORTH: "F.", LEMMA: "Fómhar"}],

    "M.Fómh.": [
        {ORTH: "M.", LEMMA: "Meán"},
        {ORTH: "Fómh.", LEMMA: "Fómhar"}],

    "R.C.": [
        {ORTH: "Rr.", LEMMA: "roimh"},
        {ORTH: "C.", LEMMA: "Críost"}],

    "r.Ch.": [
        {ORTH: "r.", LEMMA: "roimh"},
        {ORTH: "Ch.", LEMMA: "Críost"}],

    "r.Chr.": [
        {ORTH: "r.", LEMMA: "roimh"},
        {ORTH: "Chr.", LEMMA: "Críost"}],

    "R.Ch.": [
        {ORTH: "R.", LEMMA: "roimh"},
        {ORTH: "Ch.", LEMMA: "Críost"}],

    "R.Chr.": [
        {ORTH: "R.", LEMMA: "roimh"},
        {ORTH: "Chr.", LEMMA: "Críost"}],

    "⁊rl.": [
        {ORTH: "⁊", LEMMA: "agus"},
        {ORTH: "rl.", LEMMA: "araile"}],

    "srl.": [
        {ORTH: "s", LEMMA: "agus"},
        {ORTH: "rl.", LEMMA: "araile"}],

}

for exc_data in [
    {ORTH: "'gus", LEMMA: "agus", NORM: "agus"},
    {ORTH: "'ach", LEMMA: "gach", NORM: "gach"},
    {ORTH: "ao'", LEMMA: "aon", NORM: "aon"},
    {ORTH: "'niar", LEMMA: "aniar", NORM: "aniar"},
    {ORTH: "'níos", LEMMA: "aníos", NORM: "aníos"},
    {ORTH: "'ndiu", LEMMA: "inniu", NORM: "inniu"},
    {ORTH: "'nocht", LEMMA: "anocht", NORM: "anocht"},
    {ORTH: "m'", LEMMA: "mo"},,
    {ORTH: "Aib.", LEMMA: "Aibreán"},
    {ORTH: "Ath.", LEMMA: "athair"},
    {ORTH: "Beal.", LEMMA: "Bealtaine"},
    {ORTH: "Co.", LEMMA: "contae"},
    {ORTH: "Ean.", LEMMA: "Eanáir"},
    {ORTH: "Feab.", LEMMA: "Feabhra"},
    {ORTH: "gCo.", LEMMA: "contae"},
    {ORTH: ".i.", LEMMA: "eadhon"},
    {ORTH: "lch.", LEMMA: "leathanach"},
    {ORTH: "Lch.", LEMMA: "leathanach"},
    {ORTH: "lgh.", LEMMA: "leathanach"},
    {ORTH: "Lgh.", LEMMA: "leathanach"},
    {ORTH: "Lún.", LEMMA: "Lúnasa"},
    {ORTH: "Már.", LEMMA: "Márta"},
    {ORTH: "Meith.", LEMMA: "Meitheamh"},
    {ORTH: "Noll.", LEMMA: "Nollaig"},
    {ORTH: "Samh.", LEMMA: "Samhain"},
    {ORTH: "tAth.", LEMMA: "athair"},
    {ORTH: "tUas.", LEMMA: "Uasal"},
    {ORTH: "teo.", LEMMA: "teoranta"},
    {ORTH: "Teo.", LEMMA: "teoranta"},
    {ORTH: "Uas.", LEMMA: "Uasal"},
    {ORTH: "uimh.", LEMMA: "uimhir"},
    {ORTH: "Uimh.", LEMMA: "uimhir"}]:
    _exc[exc_data[ORTH]] = [dict(exc_data)],

for orth in [
    "d'"]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = dict(_exc)
