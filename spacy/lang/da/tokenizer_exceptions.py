# encoding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM, TAG, ADP, PUNCT


_exc = {}

for exc_data in [
    {ORTH: "Kbh.", LEMMA: "København", NORM: "København"},
    {ORTH: "Jan.", LEMMA: "januar", NORM: "januar"},
    {ORTH: "Feb.", LEMMA: "februar", NORM: "februar"},
    {ORTH: "Mar.", LEMMA: "marts", NORM: "marts"},
    {ORTH: "Apr.", LEMMA: "april", NORM: "april"},
    {ORTH: "Maj.", LEMMA: "maj", NORM: "maj"},
    {ORTH: "Jun.", LEMMA: "juni", NORM: "juni"},
    {ORTH: "Jul.", LEMMA: "juli", NORM: "juli"},
    {ORTH: "Aug.", LEMMA: "august", NORM: "august"},
    {ORTH: "Sep.", LEMMA: "september", NORM: "september"},
    {ORTH: "Okt.", LEMMA: "oktober", NORM: "oktober"},
    {ORTH: "Nov.", LEMMA: "november", NORM: "november"},
    {ORTH: "Dec.", LEMMA: "december", NORM: "december"}]:
    _exc[exc_data[ORTH]] = [exc_data]

for orth in [
    "A/S", "beg.", "bl.a.", "ca.", "d.s.s.", "dvs.", "f.eks.", "fr.", "hhv.",
    "if.", "iflg.", "m.a.o.", "mht.", "min.", "osv.", "pga.", "resp.", "self.",
    "t.o.m.", "vha.", ""]:
    _exc[orth] = [{ORTH: orth}]

_custom_base_exc = {
    "i.": [
        {ORTH: "i", LEMMA: "i", NORM: "i"},
        {ORTH: ".", TAG: PUNCT}]
}
_exc.update(_custom_base_exc)


TOKENIZER_EXCEPTIONS = _exc
