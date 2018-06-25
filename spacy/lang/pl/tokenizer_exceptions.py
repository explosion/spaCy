# encoding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, POS, ADV, ADJ, NOUN, ADP


_exc = {}

for exc_data in [
    {ORTH: "m.in.", LEMMA: "między innymi", POS: ADV},
    {ORTH: "inż.", LEMMA: "inżynier", POS: NOUN},
    {ORTH: "mgr.", LEMMA: "magister", POS: NOUN},
    {ORTH: "tzn.", LEMMA: "to znaczy", POS: ADV},
    {ORTH: "tj.", LEMMA: "to jest", POS: ADV},
    {ORTH: "tzw.", LEMMA: "tak zwany", POS: ADJ},
    {ORTH: "adw.", LEMMA: "adwokat", POS: NOUN},
    {ORTH: "afr.", LEMMA: "afrykański", POS: ADJ},
    {ORTH: "c.b.d.o.", LEMMA: "co było do okazania", POS: ADV},
    {ORTH: "cbdu.", LEMMA: "co było do udowodnienia", POS: ADV},
    {ORTH: "mn.w.", LEMMA: "mniej więcej", POS: ADV},
    {ORTH: "nt.", LEMMA: "na temat", POS: ADP},
    {ORTH: "ok.", LEMMA: "około"},
    {ORTH: "n.p.u.", LEMMA: "na psa urok"},
    {ORTH: "ww.", LEMMA: "wyżej wymieniony", POS: ADV}]:
    _exc[exc_data[ORTH]] = [exc_data]

for orth in [
    "w.", "r.", "br.", "bm.", "b.r.", "amer.", "am.", "bdb.", "św.", "p.", "lit.",
    "wym.", "czyt.", "daw.", "d.", "zob.", "gw.", "dn.", "dyr.", "im.", "mł.",
    "min.", "dot.", "muz.", "k.k.", "k.p.a.", "k.p.c.", "n.p.m.", "p.p.m.", "nb.",
    "ob.", "n.e.", "p.n.e.", "zw.", "zool.", "zach.", "żarg.", "żart.", "wzgl.",
    "wyj.", "xx.", "ks.", "x.", "wyd.", "wsch.", "o.o."]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc
