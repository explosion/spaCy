# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA

# Source https://www.cs.tut.fi/~jkorpela/kielenopas/5.5.html

TOKENIZER_EXCEPTIONS = {
    "aik.": [
        {ORTH: "aik.", LEMMA: "aikaisempi"}
    ],
    "alk.": [
        {ORTH: "alk.", LEMMA: "alkaen"}
    ],
    "alv.": [
        {ORTH: "alv.", LEMMA: "arvonlisävero"}
    ],
    "ark.": [
        {ORTH: "ark.", LEMMA: "arkisin"}
    ],
    "as.": [
        {ORTH: "as.", LEMMA: "asunto"}
    ],
    "ed.": [
        {ORTH: "ed.", LEMMA: "edellinen"}
    ],
    "esim.": [
        {ORTH: "esim.", LEMMA: "esimerkki"}
    ],
    "huom.": [
        {ORTH: "huom.", LEMMA: "huomautus"}
    ],
    "jne.": [
        {ORTH: "jne.", LEMMA: "ja niin edelleen"}
    ],
    "joht.": [
        {ORTH: "joht.", LEMMA: "johtaja"}
    ],
    "k.": [
        {ORTH: "k.", LEMMA: "kuollut"}
    ],
    "ks.": [
        {ORTH: "ks.", LEMMA: "katso"}
    ],
    "lk.": [
        {ORTH: "lk.", LEMMA: "luokka"}
    ],
    "lkm.": [
        {ORTH: "lkm.", LEMMA: "lukumäärä"}
    ],
    "lyh.": [
        {ORTH: "lyh.", LEMMA: "lyhenne"}
    ],
    "läh.": [
        {ORTH: "läh.", LEMMA: "lähettäjä"}
    ],
    "miel.": [
        {ORTH: "miel.", LEMMA: "mieluummin"}
    ],
    "milj.": [
        {ORTH: "milj.", LEMMA: "miljoona"}
    ],
    "mm.": [
        {ORTH: "mm.", LEMMA: "muun muassa"}
    ],
    "myöh.": [
        {ORTH: "myöh.", LEMMA: "myöhempi"}
    ],
    "n.": [
        {ORTH: "n.", LEMMA: "noin"}
    ],
    "nimim.": [
        {ORTH: "nimim.", LEMMA: "nimimerkki"}
    ],
    "ns.": [
        {ORTH: "ns.", LEMMA: "niin sanottu"}
    ],
    "nyk.": [
        {ORTH: "nyk.", LEMMA: "nykyinen"}
    ],
    "oik.": [
        {ORTH: "oik.", LEMMA: "oikealla"}
    ],
    "os.": [
        {ORTH: "os.", LEMMA: "osoite"}
    ],
    "p.": [
        {ORTH: "p.", LEMMA: "päivä"}
    ],
    "par.": [
        {ORTH: "par.", LEMMA: "paremmin"}
    ],
    "per.": [
        {ORTH: "per.", LEMMA: "perustettu"}
    ],
    "pj.": [
        {ORTH: "pj.", LEMMA: "puheenjohtaja"}
    ],
    "puh.joht.": [
        {ORTH: "puh.joht.", LEMMA: "puheenjohtaja"}
    ],
    "prof.": [
        {ORTH: "prof.", LEMMA: "professori"}
    ],
    "puh.": [
        {ORTH: "puh.", LEMMA: "puhelin"}
    ],
    "pvm.": [
        {ORTH: "pvm.", LEMMA: "päivämäärä"}
    ],
    "rak.": [
        {ORTH: "rak.", LEMMA: "rakennettu"}
    ],
    "ry.": [
        {ORTH: "ry.", LEMMA: "rekisteröity yhdistys"}
    ],
    "s.": [
        {ORTH: "s.", LEMMA: "sivu"}
    ],
    "siht.": [
        {ORTH: "siht.", LEMMA: "sihteeri"}
    ],
    "synt.": [
        {ORTH: "synt.", LEMMA: "syntynyt"}
    ],
    "t.": [
        {ORTH: "t.", LEMMA: "toivoo"}
    ],
    "tark.": [
        {ORTH: "tark.", LEMMA: "tarkastanut"}
    ],
    "til.": [
        {ORTH: "til.", LEMMA: "tilattu"}
    ],
    "tms.": [
        {ORTH: "tms.", LEMMA: "tai muuta sellaista"}
    ],
    "toim.": [
        {ORTH: "toim.", LEMMA: "toimittanut"}
    ],
    "v.": [
        {ORTH: "v.", LEMMA: "vuosi"}
    ],
    "vas.": [
        {ORTH: "vas.", LEMMA: "vasen"}
    ],
    "vast.": [
        {ORTH: "vast.", LEMMA: "vastaus"}
    ],
    "vrt.": [
        {ORTH: "vrt.", LEMMA: "vertaa"}
    ],
    "yht.": [
        {ORTH: "yht.", LEMMA: "yhteensä"}
    ],
    "yl.": [
        {ORTH: "yl.", LEMMA: "yleinen"}
    ],
    "ym.": [
        {ORTH: "ym.", LEMMA: "ynnä muuta"}
    ],
    "yms.": [
        {ORTH: "yms.", LEMMA: "ynnä muuta sellaista"}
    ],
    "yo.": [
        {ORTH: "yo.", LEMMA: "ylioppilas"}
    ],
    "yliopp.": [
        {ORTH: "yliopp.", LEMMA: "ylioppilas"}
    ],
    "ao.": [
        {ORTH: "ao.", LEMMA: "asianomainen"}
    ],
    "em.": [
        {ORTH: "em.", LEMMA: "edellä mainittu"}
    ],
    "ko.": [
        {ORTH: "ko.", LEMMA: "kyseessä oleva"}
    ],
    "ml.": [
        {ORTH: "ml.", LEMMA: "mukaan luettuna"}
    ],
    "po.": [
        {ORTH: "po.", LEMMA: "puheena oleva"}
    ],
    "so.": [
        {ORTH: "so.", LEMMA: "se on"}
    ],
    "ts.": [
        {ORTH: "ts.", LEMMA: "toisin sanoen"}
    ],
    "vm.": [
        {ORTH: "vm.", LEMMA: "viimeksi mainittu"}
    ],
    "siht.": [
        {ORTH: "siht.", LEMMA: "sihteeri"}
    ],
    "srk.": [
        {ORTH: "srk.", LEMMA: "seurakunta"}
    ]
}
