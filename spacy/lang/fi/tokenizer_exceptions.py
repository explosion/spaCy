# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA


_exc = {}


# Source https://www.cs.tut.fi/~jkorpela/kielenopas/5.5.html
for exc_data in [
    {ORTH: "aik.", LEMMA: "aikaisempi"},
    {ORTH: "alk.", LEMMA: "alkaen"},
    {ORTH: "alv.", LEMMA: "arvonlisävero"},
    {ORTH: "ark.", LEMMA: "arkisin"},
    {ORTH: "as.", LEMMA: "asunto"},
    {ORTH: "ed.", LEMMA: "edellinen"},
    {ORTH: "esim.", LEMMA: "esimerkki"},
    {ORTH: "huom.", LEMMA: "huomautus"},
    {ORTH: "jne.", LEMMA: "ja niin edelleen"},
    {ORTH: "joht.", LEMMA: "johtaja"},
    {ORTH: "k.", LEMMA: "kuollut"},
    {ORTH: "ks.", LEMMA: "katso"},
    {ORTH: "lk.", LEMMA: "luokka"},
    {ORTH: "lkm.", LEMMA: "lukumäärä"},
    {ORTH: "lyh.", LEMMA: "lyhenne"},
    {ORTH: "läh.", LEMMA: "lähettäjä"},
    {ORTH: "miel.", LEMMA: "mieluummin"},
    {ORTH: "milj.", LEMMA: "miljoona"},
    {ORTH: "mm.", LEMMA: "muun muassa"},
    {ORTH: "myöh.", LEMMA: "myöhempi"},
    {ORTH: "n.", LEMMA: "noin"},
    {ORTH: "nimim.", LEMMA: "nimimerkki"},
    {ORTH: "ns.", LEMMA: "niin sanottu"},
    {ORTH: "nyk.", LEMMA: "nykyinen"},
    {ORTH: "oik.", LEMMA: "oikealla"},
    {ORTH: "os.", LEMMA: "osoite"},
    {ORTH: "p.", LEMMA: "päivä"},
    {ORTH: "par.", LEMMA: "paremmin"},
    {ORTH: "per.", LEMMA: "perustettu"},
    {ORTH: "pj.", LEMMA: "puheenjohtaja"},
    {ORTH: "puh.joht.", LEMMA: "puheenjohtaja"},
    {ORTH: "prof.", LEMMA: "professori"},
    {ORTH: "puh.", LEMMA: "puhelin"},
    {ORTH: "pvm.", LEMMA: "päivämäärä"},
    {ORTH: "rak.", LEMMA: "rakennettu"},
    {ORTH: "ry.", LEMMA: "rekisteröity yhdistys"},
    {ORTH: "s.", LEMMA: "sivu"},
    {ORTH: "siht.", LEMMA: "sihteeri"},
    {ORTH: "synt.", LEMMA: "syntynyt"},
    {ORTH: "t.", LEMMA: "toivoo"},
    {ORTH: "tark.", LEMMA: "tarkastanut"},
    {ORTH: "til.", LEMMA: "tilattu"},
    {ORTH: "tms.", LEMMA: "tai muuta sellaista"},
    {ORTH: "toim.", LEMMA: "toimittanut"},
    {ORTH: "v.", LEMMA: "vuosi"},
    {ORTH: "vas.", LEMMA: "vasen"},
    {ORTH: "vast.", LEMMA: "vastaus"},
    {ORTH: "vrt.", LEMMA: "vertaa"},
    {ORTH: "yht.", LEMMA: "yhteensä"},
    {ORTH: "yl.", LEMMA: "yleinen"},
    {ORTH: "ym.", LEMMA: "ynnä muuta"},
    {ORTH: "yms.", LEMMA: "ynnä muuta sellaista"},
    {ORTH: "yo.", LEMMA: "ylioppilas"},
    {ORTH: "yliopp.", LEMMA: "ylioppilas"},
    {ORTH: "ao.", LEMMA: "asianomainen"},
    {ORTH: "em.", LEMMA: "edellä mainittu"},
    {ORTH: "ko.", LEMMA: "kyseessä oleva"},
    {ORTH: "ml.", LEMMA: "mukaan luettuna"},
    {ORTH: "po.", LEMMA: "puheena oleva"},
    {ORTH: "so.", LEMMA: "se on"},
    {ORTH: "ts.", LEMMA: "toisin sanoen"},
    {ORTH: "vm.", LEMMA: "viimeksi mainittu"},
    {ORTH: "srk.", LEMMA: "seurakunta"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


TOKENIZER_EXCEPTIONS = _exc
