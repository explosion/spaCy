# encoding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA


_exc = {}


for orth in [
    "A/S", "beg.", "bl.a.", "ca.", "d.s.s.", "dvs.", "f.eks.", "fr.", "hhv.",
    "if.", "iflg.", "m.a.o.", "mht.", "min.", "osv.", "pga.", "resp.", "self.",
    "t.o.m.", "vha.", ""]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = dict(_exc)
