# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA, DET_LEMMA


TOKENIZER_EXCEPTIONS = {
    "\\n": [
        {ORTH: "\\n", LEMMA: "<nl>", TAG: "SP"}
    ],

    "\\t": [
        {ORTH: "\\t", LEMMA: "<tab>", TAG: "SP"}
    ],

    "'S": [
        {ORTH: "'S", LEMMA: PRON_LEMMA, TAG: "PPER"}
    ],

    "'n": [
        {ORTH: "'n", LEMMA: DET_LEMMA, NORM: "ein"}
    ],

    "'ne": [
        {ORTH: "'ne", LEMMA: DET_LEMMA, NORM: "eine"}
    ],

    "'nen": [
        {ORTH: "'nen", LEMMA: DET_LEMMA, NORM: "einen"}
    ],

    "'nem": [
        {ORTH: "'nem", LEMMA: DET_LEMMA, NORM: "einem"}
    ],

    "'s": [
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER"}
    ],

    "Abb.": [
        {ORTH: "Abb.", LEMMA: "Abbildung"}
    ],

    "Abk.": [
        {ORTH: "Abk.", LEMMA: "Abkürzung"}
    ],

    "Abt.": [
        {ORTH: "Abt.", LEMMA: "Abteilung"}
    ],

    "Apr.": [
        {ORTH: "Apr.", LEMMA: "April"}
    ],

    "Aug.": [
        {ORTH: "Aug.", LEMMA: "August"}
    ],

    "Bd.": [
        {ORTH: "Bd.", LEMMA: "Band"}
    ],

    "Betr.": [
        {ORTH: "Betr.", LEMMA: "Betreff"}
    ],

    "Bf.": [
        {ORTH: "Bf.", LEMMA: "Bahnhof"}
    ],

    "Bhf.": [
        {ORTH: "Bhf.", LEMMA: "Bahnhof"}
    ],

    "Bsp.": [
        {ORTH: "Bsp.", LEMMA: "Beispiel"}
    ],

    "Dez.": [
        {ORTH: "Dez.", LEMMA: "Dezember"}
    ],

    "Di.": [
        {ORTH: "Di.", LEMMA: "Dienstag"}
    ],

    "Do.": [
        {ORTH: "Do.", LEMMA: "Donnerstag"}
    ],

    "Fa.": [
        {ORTH: "Fa.", LEMMA: "Firma"}
    ],

    "Fam.": [
        {ORTH: "Fam.", LEMMA: "Familie"}
    ],

    "Feb.": [
        {ORTH: "Feb.", LEMMA: "Februar"}
    ],

    "Fr.": [
        {ORTH: "Fr.", LEMMA: "Frau"}
    ],

    "Frl.": [
        {ORTH: "Frl.", LEMMA: "Fräulein"}
    ],

    "Hbf.": [
        {ORTH: "Hbf.", LEMMA: "Hauptbahnhof"}
    ],

    "Hr.": [
        {ORTH: "Hr.", LEMMA: "Herr"}
    ],

    "Hrn.": [
        {ORTH: "Hrn.", LEMMA: "Herr"}
    ],

    "Jan.": [
        {ORTH: "Jan.", LEMMA: "Januar"}
    ],

    "Jh.": [
        {ORTH: "Jh.", LEMMA: "Jahrhundert"}
    ],

    "Jhd.": [
        {ORTH: "Jhd.", LEMMA: "Jahrhundert"}
    ],

    "Jul.": [
        {ORTH: "Jul.", LEMMA: "Juli"}
    ],

    "Jun.": [
        {ORTH: "Jun.", LEMMA: "Juni"}
    ],

    "Mi.": [
        {ORTH: "Mi.", LEMMA: "Mittwoch"}
    ],

    "Mio.": [
        {ORTH: "Mio.", LEMMA: "Million"}
    ],

    "Mo.": [
        {ORTH: "Mo.", LEMMA: "Montag"}
    ],

    "Mrd.": [
        {ORTH: "Mrd.", LEMMA: "Milliarde"}
    ],

    "Mrz.": [
        {ORTH: "Mrz.", LEMMA: "März"}
    ],

    "MwSt.": [
        {ORTH: "MwSt.", LEMMA: "Mehrwertsteuer"}
    ],

    "Mär.": [
        {ORTH: "Mär.", LEMMA: "März"}
    ],

    "Nov.": [
        {ORTH: "Nov.", LEMMA: "November"}
    ],

    "Nr.": [
        {ORTH: "Nr.", LEMMA: "Nummer"}
    ],

    "Okt.": [
        {ORTH: "Okt.", LEMMA: "Oktober"}
    ],

    "Orig.": [
        {ORTH: "Orig.", LEMMA: "Original"}
    ],

    "Pkt.": [
        {ORTH: "Pkt.", LEMMA: "Punkt"}
    ],

    "Prof.": [
        {ORTH: "Prof.", LEMMA: "Professor"}
    ],

    "Red.": [
        {ORTH: "Red.", LEMMA: "Redaktion"}
    ],

    "S'": [
        {ORTH: "S'", LEMMA: PRON_LEMMA, TAG: "PPER"}
    ],

    "Sa.": [
        {ORTH: "Sa.", LEMMA: "Samstag"}
    ],

    "Sep.": [
        {ORTH: "Sep.", LEMMA: "September"}
    ],

    "Sept.": [
        {ORTH: "Sept.", LEMMA: "September"}
    ],

    "So.": [
        {ORTH: "So.", LEMMA: "Sonntag"}
    ],

    "Std.": [
        {ORTH: "Std.", LEMMA: "Stunde"}
    ],

    "Str.": [
        {ORTH: "Str.", LEMMA: "Straße"}
    ],

    "Tel.": [
        {ORTH: "Tel.", LEMMA: "Telefon"}
    ],

    "Tsd.": [
        {ORTH: "Tsd.", LEMMA: "Tausend"}
    ],

    "Univ.": [
        {ORTH: "Univ.", LEMMA: "Universität"}
    ],

    "abzgl.": [
        {ORTH: "abzgl.", LEMMA: "abzüglich"}
    ],

    "allg.": [
        {ORTH: "allg.", LEMMA: "allgemein"}
    ],

    "auf'm": [
        {ORTH: "auf", LEMMA: "auf"},
        {ORTH: "'m", LEMMA: DET_LEMMA, NORM: "dem" }
    ],

    "bspw.": [
        {ORTH: "bspw.", LEMMA: "beispielsweise"}
    ],

    "bzgl.": [
        {ORTH: "bzgl.", LEMMA: "bezüglich"}
    ],

    "bzw.": [
        {ORTH: "bzw.", LEMMA: "beziehungsweise"}
    ],

    "d.h.": [
        {ORTH: "d.h.", LEMMA: "das heißt"}
    ],

    "dgl.": [
        {ORTH: "dgl.", LEMMA: "dergleichen"}
    ],

    "du's": [
        {ORTH: "du", LEMMA: PRON_LEMMA, TAG: "PPER"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER", NORM: "es"}
    ],

    "ebd.": [
        {ORTH: "ebd.", LEMMA: "ebenda"}
    ],

    "eigtl.": [
        {ORTH: "eigtl.", LEMMA: "eigentlich"}
    ],

    "engl.": [
        {ORTH: "engl.", LEMMA: "englisch"}
    ],

    "er's": [
        {ORTH: "er", LEMMA: PRON_LEMMA, TAG: "PPER"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER", NORM: "es"}
    ],

    "evtl.": [
        {ORTH: "evtl.", LEMMA: "eventuell"}
    ],

    "frz.": [
        {ORTH: "frz.", LEMMA: "französisch"}
    ],

    "gegr.": [
        {ORTH: "gegr.", LEMMA: "gegründet"}
    ],

    "ggf.": [
        {ORTH: "ggf.", LEMMA: "gegebenenfalls"}
    ],

    "ggfs.": [
        {ORTH: "ggfs.", LEMMA: "gegebenenfalls"}
    ],

    "ggü.": [
        {ORTH: "ggü.", LEMMA: "gegenüber"}
    ],

    "hinter'm": [
        {ORTH: "hinter", LEMMA: "hinter"},
        {ORTH: "'m", LEMMA: DET_LEMMA, NORM: "dem"}
    ],

    "i.O.": [
        {ORTH: "i.O.", LEMMA: "in Ordnung"}
    ],

    "i.d.R.": [
        {ORTH: "i.d.R.", LEMMA: "in der Regel"}
    ],

    "ich's": [
        {ORTH: "ich", LEMMA: PRON_LEMMA, TAG: "PPER"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER", NORM: "es"}
    ],

    "ihr's": [
        {ORTH: "ihr", LEMMA: PRON_LEMMA, TAG: "PPER"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER", NORM: "es"}
    ],

    "incl.": [
        {ORTH: "incl.", LEMMA: "inklusive"}
    ],

    "inkl.": [
        {ORTH: "inkl.", LEMMA: "inklusive"}
    ],

    "insb.": [
        {ORTH: "insb.", LEMMA: "insbesondere"}
    ],

    "kath.": [
        {ORTH: "kath.", LEMMA: "katholisch"}
    ],

    "lt.": [
        {ORTH: "lt.", LEMMA: "laut"}
    ],

    "max.": [
        {ORTH: "max.", LEMMA: "maximal"}
    ],

    "min.": [
        {ORTH: "min.", LEMMA: "minimal"}
    ],

    "mind.": [
        {ORTH: "mind.", LEMMA: "mindestens"}
    ],

    "mtl.": [
        {ORTH: "mtl.", LEMMA: "monatlich"}
    ],

    "n.Chr.": [
        {ORTH: "n.Chr.", LEMMA: "nach Christus"}
    ],

    "orig.": [
        {ORTH: "orig.", LEMMA: "original"}
    ],

    "röm.": [
        {ORTH: "röm.", LEMMA: "römisch"}
    ],

    "s'": [
        {ORTH: "s'", LEMMA: PRON_LEMMA, TAG: "PPER"}
    ],

    "s.o.": [
        {ORTH: "s.o.", LEMMA: "siehe oben"}
    ],

    "sie's": [
        {ORTH: "sie", LEMMA: PRON_LEMMA, TAG: "PPER"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER", NORM: "es"}
    ],

    "sog.": [
        {ORTH: "sog.", LEMMA: "so genannt"}
    ],

    "stellv.": [
        {ORTH: "stellv.", LEMMA: "stellvertretend"}
    ],

    "tägl.": [
        {ORTH: "tägl.", LEMMA: "täglich"}
    ],

    "u.U.": [
        {ORTH: "u.U.", LEMMA: "unter Umständen"}
    ],

    "u.s.w.": [
        {ORTH: "u.s.w.", LEMMA: "und so weiter"}
    ],

    "u.v.m.": [
        {ORTH: "u.v.m.", LEMMA: "und vieles mehr"}
    ],

    "unter'm": [
        {ORTH: "unter", LEMMA: "unter"},
        {ORTH: "'m", LEMMA: DET_LEMMA, NORM: "dem"}
    ],

    "usf.": [
        {ORTH: "usf.", LEMMA: "und so fort"}
    ],

    "usw.": [
        {ORTH: "usw.", LEMMA: "und so weiter"}
    ],

    "uvm.": [
        {ORTH: "uvm.", LEMMA: "und vieles mehr"}
    ],

    "v.Chr.": [
        {ORTH: "v.Chr.", LEMMA: "vor Christus"}
    ],

    "v.a.": [
        {ORTH: "v.a.", LEMMA: "vor allem"}
    ],

    "v.l.n.r.": [
        {ORTH: "v.l.n.r.", LEMMA: "von links nach rechts"}
    ],

    "vgl.": [
        {ORTH: "vgl.", LEMMA: "vergleiche"}
    ],

    "vllt.": [
        {ORTH: "vllt.", LEMMA: "vielleicht"}
    ],

    "vlt.": [
        {ORTH: "vlt.", LEMMA: "vielleicht"}
    ],

    "vor'm": [
        {ORTH: "vor", LEMMA: "vor"},
        {ORTH: "'m", LEMMA: DET_LEMMA, NORM: "dem"}
    ],

    "wir's": [
        {ORTH: "wir", LEMMA: PRON_LEMMA, TAG: "PPER"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER", NORM: "es"}
    ],

    "z.B.": [
        {ORTH: "z.B.", LEMMA: "zum Beispiel"}
    ],

    "z.Bsp.": [
        {ORTH: "z.Bsp.", LEMMA: "zum Beispiel"}
    ],

    "z.T.": [
        {ORTH: "z.T.", LEMMA: "zum Teil"}
    ],

    "z.Z.": [
        {ORTH: "z.Z.", LEMMA: "zur Zeit"}
    ],

    "z.Zt.": [
        {ORTH: "z.Zt.", LEMMA: "zur Zeit"}
    ],

    "z.b.": [
        {ORTH: "z.b.", LEMMA: "zum Beispiel"}
    ],

    "zzgl.": [
        {ORTH: "zzgl.", LEMMA: "zuzüglich"}
    ],

    "österr.": [
        {ORTH: "österr.", LEMMA: "österreichisch"}
    ],

    "über'm": [
        {ORTH: "über", LEMMA: "über"},
        {ORTH: "'m", LEMMA: DET_LEMMA, NORM: "dem"}
    ]
}


ORTH_ONLY = [
    "'",
    "\\\")",
    "<space>",
    "a.",
    "ä.",
    "A.C.",
    "a.D.",
    "A.D.",
    "A.G.",
    "a.M.",
    "a.Z.",
    "Abs.",
    "adv.",
    "al.",
    "b.",
    "B.A.",
    "B.Sc.",
    "betr.",
    "biol.",
    "Biol.",
    "c.",
    "ca.",
    "Chr.",
    "Cie.",
    "co.",
    "Co.",
    "d.",
    "D.C.",
    "Dipl.-Ing.",
    "Dipl.",
    "Dr.",
    "e.",
    "e.g.",
    "e.V.",
    "ehem.",
    "entspr.",
    "erm.",
    "etc.",
    "ev.",
    "f.",
    "g.",
    "G.m.b.H.",
    "geb.",
    "Gebr.",
    "gem.",
    "h.",
    "h.c.",
    "Hg.",
    "hrsg.",
    "Hrsg.",
    "i.",
    "i.A.",
    "i.e.",
    "i.G.",
    "i.Tr.",
    "i.V.",
    "Ing.",
    "j.",
    "jr.",
    "Jr.",
    "jun.",
    "jur.",
    "k.",
    "K.O.",
    "l.",
    "L.A.",
    "lat.",
    "m.",
    "M.A.",
    "m.E.",
    "m.M.",
    "M.Sc.",
    "Mr.",
    "n.",
    "N.Y.",
    "N.Y.C.",
    "nat.",
    "ö."
    "o.",
    "o.a.",
    "o.ä.",
    "o.g.",
    "o.k.",
    "O.K.",
    "p.",
    "p.a.",
    "p.s.",
    "P.S.",
    "pers.",
    "phil.",
    "q.",
    "q.e.d.",
    "r.",
    "R.I.P.",
    "rer.",
    "s.",
    "sen.",
    "St.",
    "std.",
    "t.",
    "u.",
    "ü.",
    "u.a.",
    "U.S.",
    "U.S.A.",
    "U.S.S.",
    "v.",
    "Vol.",
    "vs.",
    "w.",
    "wiss.",
    "x.",
    "y.",
    "z."
]
