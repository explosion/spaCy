# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, TAG, NORM
from ...deprecated import PRON_LEMMA


_exc = {
    "auf'm": [
        {ORTH: "auf", LEMMA: "auf"},
        {ORTH: "'m", LEMMA: "der", NORM: "dem" }],

    "du's": [
        {ORTH: "du", LEMMA: PRON_LEMMA, TAG: "PPER"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER", NORM: "es"}],

    "er's": [
        {ORTH: "er", LEMMA: PRON_LEMMA, TAG: "PPER"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER", NORM: "es"}],

    "hinter'm": [
        {ORTH: "hinter", LEMMA: "hinter"},
        {ORTH: "'m", LEMMA: "der", NORM: "dem"}],

    "ich's": [
        {ORTH: "ich", LEMMA: PRON_LEMMA, TAG: "PPER"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER", NORM: "es"}],

    "ihr's": [
        {ORTH: "ihr", LEMMA: PRON_LEMMA, TAG: "PPER"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER", NORM: "es"}],

    "sie's": [
        {ORTH: "sie", LEMMA: PRON_LEMMA, TAG: "PPER"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER", NORM: "es"}],

    "unter'm": [
        {ORTH: "unter", LEMMA: "unter"},
        {ORTH: "'m", LEMMA: "der", NORM: "dem"}],

    "vor'm": [
        {ORTH: "vor", LEMMA: "vor"},
        {ORTH: "'m", LEMMA: "der", NORM: "dem"}],

    "wir's": [
        {ORTH: "wir", LEMMA: PRON_LEMMA, TAG: "PPER"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER", NORM: "es"}],

    "über'm": [
        {ORTH: "über", LEMMA: "über"},
        {ORTH: "'m", LEMMA: "der", NORM: "dem"}]
}


for exc_data in [
    {ORTH: "'S", LEMMA: PRON_LEMMA, TAG: "PPER"},
    {ORTH: "'s", LEMMA: PRON_LEMMA, TAG: "PPER"},
    {ORTH: "S'", LEMMA: PRON_LEMMA, TAG: "PPER"},
    {ORTH: "s'", LEMMA: PRON_LEMMA, TAG: "PPER"},
    {ORTH: "'n", LEMMA: "ein", NORM: "ein"},
    {ORTH: "'ne", LEMMA: "eine", NORM: "eine"},
    {ORTH: "'nen", LEMMA: "ein", NORM: "einen"},
    {ORTH: "'nem", LEMMA: "ein", NORM: "einem"},
    {ORTH: "Abb.", LEMMA: "Abbildung"},
    {ORTH: "Abk.", LEMMA: "Abkürzung"},
    {ORTH: "Abt.", LEMMA: "Abteilung"},
    {ORTH: "Apr.", LEMMA: "April"},
    {ORTH: "Aug.", LEMMA: "August"},
    {ORTH: "Bd.", LEMMA: "Band"},
    {ORTH: "Betr.", LEMMA: "Betreff"},
    {ORTH: "Bf.", LEMMA: "Bahnhof"},
    {ORTH: "Bhf.", LEMMA: "Bahnhof"},
    {ORTH: "Bsp.", LEMMA: "Beispiel"},
    {ORTH: "Dez.", LEMMA: "Dezember"},
    {ORTH: "Di.", LEMMA: "Dienstag"},
    {ORTH: "Do.", LEMMA: "Donnerstag"},
    {ORTH: "Fa.", LEMMA: "Firma"},
    {ORTH: "Fam.", LEMMA: "Familie"},
    {ORTH: "Feb.", LEMMA: "Februar"},
    {ORTH: "Fr.", LEMMA: "Frau"},
    {ORTH: "Frl.", LEMMA: "Fräulein"},
    {ORTH: "Hbf.", LEMMA: "Hauptbahnhof"},
    {ORTH: "Hr.", LEMMA: "Herr"},
    {ORTH: "Hrn.", LEMMA: "Herr"},
    {ORTH: "Jan.", LEMMA: "Januar"},
    {ORTH: "Jh.", LEMMA: "Jahrhundert"},
    {ORTH: "Jhd.", LEMMA: "Jahrhundert"},
    {ORTH: "Jul.", LEMMA: "Juli"},
    {ORTH: "Jun.", LEMMA: "Juni"},
    {ORTH: "Mi.", LEMMA: "Mittwoch"},
    {ORTH: "Mio.", LEMMA: "Million"},
    {ORTH: "Mo.", LEMMA: "Montag"},
    {ORTH: "Mrd.", LEMMA: "Milliarde"},
    {ORTH: "Mrz.", LEMMA: "März"},
    {ORTH: "MwSt.", LEMMA: "Mehrwertsteuer"},
    {ORTH: "Mär.", LEMMA: "März"},
    {ORTH: "Nov.", LEMMA: "November"},
    {ORTH: "Nr.", LEMMA: "Nummer"},
    {ORTH: "Okt.", LEMMA: "Oktober"},
    {ORTH: "Orig.", LEMMA: "Original"},
    {ORTH: "Pkt.", LEMMA: "Punkt"},
    {ORTH: "Prof.", LEMMA: "Professor"},
    {ORTH: "Red.", LEMMA: "Redaktion"},
    {ORTH: "Sa.", LEMMA: "Samstag"},
    {ORTH: "Sep.", LEMMA: "September"},
    {ORTH: "Sept.", LEMMA: "September"},
    {ORTH: "So.", LEMMA: "Sonntag"},
    {ORTH: "Std.", LEMMA: "Stunde"},
    {ORTH: "Str.", LEMMA: "Straße"},
    {ORTH: "Tel.", LEMMA: "Telefon"},
    {ORTH: "Tsd.", LEMMA: "Tausend"},
    {ORTH: "Univ.", LEMMA: "Universität"},
    {ORTH: "abzgl.", LEMMA: "abzüglich"},
    {ORTH: "allg.", LEMMA: "allgemein"},
    {ORTH: "bspw.", LEMMA: "beispielsweise"},
    {ORTH: "bzgl.", LEMMA: "bezüglich"},
    {ORTH: "bzw.", LEMMA: "beziehungsweise"},
    {ORTH: "d.h.", LEMMA: "das heißt"},
    {ORTH: "dgl.", LEMMA: "dergleichen"},
    {ORTH: "ebd.", LEMMA: "ebenda"},
    {ORTH: "eigtl.", LEMMA: "eigentlich"},
    {ORTH: "engl.", LEMMA: "englisch"},
    {ORTH: "evtl.", LEMMA: "eventuell"},
    {ORTH: "frz.", LEMMA: "französisch"},
    {ORTH: "gegr.", LEMMA: "gegründet"},
    {ORTH: "ggf.", LEMMA: "gegebenenfalls"},
    {ORTH: "ggfs.", LEMMA: "gegebenenfalls"},
    {ORTH: "ggü.", LEMMA: "gegenüber"},
    {ORTH: "i.O.", LEMMA: "in Ordnung"},
    {ORTH: "i.d.R.", LEMMA: "in der Regel"},
    {ORTH: "incl.", LEMMA: "inklusive"},
    {ORTH: "inkl.", LEMMA: "inklusive"},
    {ORTH: "insb.", LEMMA: "insbesondere"},
    {ORTH: "kath.", LEMMA: "katholisch"},
    {ORTH: "lt.", LEMMA: "laut"},
    {ORTH: "max.", LEMMA: "maximal"},
    {ORTH: "min.", LEMMA: "minimal"},
    {ORTH: "mind.", LEMMA: "mindestens"},
    {ORTH: "mtl.", LEMMA: "monatlich"},
    {ORTH: "n.Chr.", LEMMA: "nach Christus"},
    {ORTH: "orig.", LEMMA: "original"},
    {ORTH: "röm.", LEMMA: "römisch"},
    {ORTH: "s.o.", LEMMA: "siehe oben"},
    {ORTH: "sog.", LEMMA: "so genannt"},
    {ORTH: "stellv.", LEMMA: "stellvertretend"},
    {ORTH: "tägl.", LEMMA: "täglich"},
    {ORTH: "u.U.", LEMMA: "unter Umständen"},
    {ORTH: "u.s.w.", LEMMA: "und so weiter"},
    {ORTH: "u.v.m.", LEMMA: "und vieles mehr"},
    {ORTH: "usf.", LEMMA: "und so fort"},
    {ORTH: "usw.", LEMMA: "und so weiter"},
    {ORTH: "uvm.", LEMMA: "und vieles mehr"},
    {ORTH: "v.Chr.", LEMMA: "vor Christus"},
    {ORTH: "v.a.", LEMMA: "vor allem"},
    {ORTH: "v.l.n.r.", LEMMA: "von links nach rechts"},
    {ORTH: "vgl.", LEMMA: "vergleiche"},
    {ORTH: "vllt.", LEMMA: "vielleicht"},
    {ORTH: "vlt.", LEMMA: "vielleicht"},
    {ORTH: "z.B.", LEMMA: "zum Beispiel"},
    {ORTH: "z.Bsp.", LEMMA: "zum Beispiel"},
    {ORTH: "z.T.", LEMMA: "zum Teil"},
    {ORTH: "z.Z.", LEMMA: "zur Zeit"},
    {ORTH: "z.Zt.", LEMMA: "zur Zeit"},
    {ORTH: "z.b.", LEMMA: "zum Beispiel"},
    {ORTH: "zzgl.", LEMMA: "zuzüglich"},
    {ORTH: "österr.", LEMMA: "österreichisch"}]:
    _exc[exc_data[ORTH]] = [dict(exc_data)]


for orth in [
    "A.C.", "a.D.", "A.D.", "A.G.", "a.M.", "a.Z.", "Abs.", "adv.", "al.",
    "B.A.", "B.Sc.", "betr.", "biol.", "Biol.", "ca.", "Chr.", "Cie.", "co.",
    "Co.", "D.C.", "Dipl.-Ing.", "Dipl.", "Dr.", "e.g.", "e.V.", "ehem.",
    "entspr.", "erm.", "etc.", "ev.", "G.m.b.H.", "geb.", "Gebr.", "gem.",
    "h.c.", "Hg.", "hrsg.", "Hrsg.", "i.A.", "i.e.", "i.G.", "i.Tr.", "i.V.",
    "Ing.", "jr.", "Jr.", "jun.", "jur.", "K.O.", "L.A.", "lat.", "M.A.",
    "m.E.", "m.M.", "M.Sc.", "Mr.", "N.Y.", "N.Y.C.", "nat.", "o.a.",
    "o.ä.", "o.g.", "o.k.", "O.K.", "p.a.", "p.s.", "P.S.", "pers.", "phil.",
    "q.e.d.", "R.I.P.", "rer.", "sen.", "St.", "std.", "u.a.", "U.S.", "U.S.A.",
    "U.S.S.", "Vol.", "vs.", "wiss."]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = dict(_exc)
