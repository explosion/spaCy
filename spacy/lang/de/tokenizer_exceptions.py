# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, TAG, NORM, PRON_LEMMA


_exc = {
    "auf'm": [
        {ORTH: "auf", LEMMA: "auf"},
        {ORTH: "'m", LEMMA: "der", NORM: "dem"}],

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
    {ORTH: "'S", LEMMA: PRON_LEMMA, NORM: "'s", TAG: "PPER"},
    {ORTH: "'s", LEMMA: PRON_LEMMA, NORM: "'s", TAG: "PPER"},
    {ORTH: "S'", LEMMA: PRON_LEMMA, NORM: "'s", TAG: "PPER"},
    {ORTH: "s'", LEMMA: PRON_LEMMA, NORM: "'s", TAG: "PPER"},
    {ORTH: "'n", LEMMA: "ein", NORM: "ein"},
    {ORTH: "'ne", LEMMA: "eine", NORM: "eine"},
    {ORTH: "'nen", LEMMA: "ein", NORM: "einen"},
    {ORTH: "'nem", LEMMA: "ein", NORM: "einem"},
    {ORTH: "Abb.", LEMMA: "Abbildung", NORM: "Abbildung"},
    {ORTH: "Abk.", LEMMA: "Abkürzung", NORM: "Abkürzung"},
    {ORTH: "Abt.", LEMMA: "Abteilung", NORM: "Abteilung"},
    {ORTH: "Apr.", LEMMA: "April", NORM: "April"},
    {ORTH: "Aug.", LEMMA: "August", NORM: "August"},
    {ORTH: "Bd.", LEMMA: "Band", NORM: "Band"},
    {ORTH: "Betr.", LEMMA: "Betreff", NORM: "Betreff"},
    {ORTH: "Bf.", LEMMA: "Bahnhof", NORM: "Bahnhof"},
    {ORTH: "Bhf.", LEMMA: "Bahnhof", NORM: "Bahnhof"},
    {ORTH: "Bsp.", LEMMA: "Beispiel", NORM: "Beispiel"},
    {ORTH: "Dez.", LEMMA: "Dezember", NORM: "Dezember"},
    {ORTH: "Di.", LEMMA: "Dienstag", NORM: "Dienstag"},
    {ORTH: "Do.", LEMMA: "Donnerstag", NORM: "Donnerstag"},
    {ORTH: "Fa.", LEMMA: "Firma", NORM: "Firma"},
    {ORTH: "Fam.", LEMMA: "Familie", NORM: "Familie"},
    {ORTH: "Feb.", LEMMA: "Februar", NORM: "Februar"},
    {ORTH: "Fr.", LEMMA: "Frau", NORM: "Frau"},
    {ORTH: "Frl.", LEMMA: "Fräulein", NORM: "Fräulein"},
    {ORTH: "Hbf.", LEMMA: "Hauptbahnhof", NORM: "Hauptbahnhof"},
    {ORTH: "Hr.", LEMMA: "Herr", NORM: "Herr"},
    {ORTH: "Hrn.", LEMMA: "Herr", NORM: "Herrn"},
    {ORTH: "Jan.", LEMMA: "Januar", NORM: "Januar"},
    {ORTH: "Jh.", LEMMA: "Jahrhundert", NORM: "Jahrhundert"},
    {ORTH: "Jhd.", LEMMA: "Jahrhundert", NORM: "Jahrhundert"},
    {ORTH: "Jul.", LEMMA: "Juli", NORM: "Juli"},
    {ORTH: "Jun.", LEMMA: "Juni", NORM: "Juni"},
    {ORTH: "Mi.", LEMMA: "Mittwoch", NORM: "Mittwoch"},
    {ORTH: "Mio.", LEMMA: "Million", NORM: "Million"},
    {ORTH: "Mo.", LEMMA: "Montag", NORM: "Montag"},
    {ORTH: "Mrd.", LEMMA: "Milliarde", NORM: "Milliarde"},
    {ORTH: "Mrz.", LEMMA: "März", NORM: "März"},
    {ORTH: "MwSt.", LEMMA: "Mehrwertsteuer", NORM: "Mehrwertsteuer"},
    {ORTH: "Mär.", LEMMA: "März", NORM: "März"},
    {ORTH: "Nov.", LEMMA: "November", NORM: "November"},
    {ORTH: "Nr.", LEMMA: "Nummer", NORM: "Nummer"},
    {ORTH: "Okt.", LEMMA: "Oktober", NORM: "Oktober"},
    {ORTH: "Orig.", LEMMA: "Original", NORM: "Original"},
    {ORTH: "Pkt.", LEMMA: "Punkt", NORM: "Punkt"},
    {ORTH: "Prof.", LEMMA: "Professor", NORM: "Professor"},
    {ORTH: "Red.", LEMMA: "Redaktion", NORM: "Redaktion"},
    {ORTH: "Sa.", LEMMA: "Samstag", NORM: "Samstag"},
    {ORTH: "Sep.", LEMMA: "September", NORM: "September"},
    {ORTH: "Sept.", LEMMA: "September", NORM: "September"},
    {ORTH: "So.", LEMMA: "Sonntag", NORM: "Sonntag"},
    {ORTH: "Std.", LEMMA: "Stunde", NORM: "Stunde"},
    {ORTH: "Str.", LEMMA: "Straße", NORM: "Straße"},
    {ORTH: "Tel.", LEMMA: "Telefon", NORM: "Telefon"},
    {ORTH: "Tsd.", LEMMA: "Tausend", NORM: "Tausend"},
    {ORTH: "Univ.", LEMMA: "Universität", NORM: "Universität"},
    {ORTH: "abzgl.", LEMMA: "abzüglich", NORM: "abzüglich"},
    {ORTH: "allg.", LEMMA: "allgemein", NORM: "allgemein"},
    {ORTH: "bspw.", LEMMA: "beispielsweise", NORM: "beispielsweise"},
    {ORTH: "bzgl.", LEMMA: "bezüglich", NORM: "bezüglich"},
    {ORTH: "bzw.", LEMMA: "beziehungsweise", NORM: "beziehungsweise"},
    {ORTH: "d.h.", LEMMA: "das heißt"},
    {ORTH: "dgl.", LEMMA: "dergleichen", NORM: "dergleichen"},
    {ORTH: "ebd.", LEMMA: "ebenda", NORM: "ebenda"},
    {ORTH: "eigtl.", LEMMA: "eigentlich", NORM: "eigentlich"},
    {ORTH: "engl.", LEMMA: "englisch", NORM: "englisch"},
    {ORTH: "evtl.", LEMMA: "eventuell", NORM: "eventuell"},
    {ORTH: "frz.", LEMMA: "französisch", NORM: "französisch"},
    {ORTH: "gegr.", LEMMA: "gegründet", NORM: "gegründet"},
    {ORTH: "ggf.", LEMMA: "gegebenenfalls", NORM: "gegebenenfalls"},
    {ORTH: "ggfs.", LEMMA: "gegebenenfalls", NORM: "gegebenenfalls"},
    {ORTH: "ggü.", LEMMA: "gegenüber", NORM: "gegenüber"},
    {ORTH: "i.O.", LEMMA: "in Ordnung"},
    {ORTH: "i.d.R.", LEMMA: "in der Regel"},
    {ORTH: "incl.", LEMMA: "inklusive", NORM: "inklusive"},
    {ORTH: "inkl.", LEMMA: "inklusive", NORM: "inklusive"},
    {ORTH: "insb.", LEMMA: "insbesondere", NORM: "insbesondere"},
    {ORTH: "kath.", LEMMA: "katholisch", NORM: "katholisch"},
    {ORTH: "lt.", LEMMA: "laut", NORM: "laut"},
    {ORTH: "max.", LEMMA: "maximal", NORM: "maximal"},
    {ORTH: "min.", LEMMA: "minimal", NORM: "minimal"},
    {ORTH: "mind.", LEMMA: "mindestens", NORM: "mindestens"},
    {ORTH: "mtl.", LEMMA: "monatlich", NORM: "monatlich"},
    {ORTH: "n.Chr.", LEMMA: "nach Christus"},
    {ORTH: "orig.", LEMMA: "original", NORM: "original"},
    {ORTH: "röm.", LEMMA: "römisch", NORM: "römisch"},
    {ORTH: "s.o.", LEMMA: "siehe oben"},
    {ORTH: "sog.", LEMMA: "so genannt"},
    {ORTH: "stellv.", LEMMA: "stellvertretend"},
    {ORTH: "tägl.", LEMMA: "täglich", NORM: "täglich"},
    {ORTH: "u.U.", LEMMA: "unter Umständen"},
    {ORTH: "u.s.w.", LEMMA: "und so weiter"},
    {ORTH: "u.v.m.", LEMMA: "und vieles mehr"},
    {ORTH: "usf.", LEMMA: "und so fort"},
    {ORTH: "usw.", LEMMA: "und so weiter"},
    {ORTH: "uvm.", LEMMA: "und vieles mehr"},
    {ORTH: "v.Chr.", LEMMA: "vor Christus"},
    {ORTH: "v.a.", LEMMA: "vor allem"},
    {ORTH: "v.l.n.r.", LEMMA: "von links nach rechts"},
    {ORTH: "vgl.", LEMMA: "vergleiche", NORM: "vergleiche"},
    {ORTH: "vllt.", LEMMA: "vielleicht", NORM: "vielleicht"},
    {ORTH: "vlt.", LEMMA: "vielleicht", NORM: "vielleicht"},
    {ORTH: "z.B.", LEMMA: "zum Beispiel"},
    {ORTH: "z.Bsp.", LEMMA: "zum Beispiel"},
    {ORTH: "z.T.", LEMMA: "zum Teil"},
    {ORTH: "z.Z.", LEMMA: "zur Zeit"},
    {ORTH: "z.Zt.", LEMMA: "zur Zeit"},
    {ORTH: "z.b.", LEMMA: "zum Beispiel"},
    {ORTH: "zzgl.", LEMMA: "zuzüglich"},
    {ORTH: "österr.", LEMMA: "österreichisch", NORM: "österreichisch"}]:
    _exc[exc_data[ORTH]] = [exc_data]


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


TOKENIZER_EXCEPTIONS = _exc
