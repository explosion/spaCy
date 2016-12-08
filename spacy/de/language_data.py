# encoding: utf8
from __future__ import unicode_literals
import re

from ..symbols import *


def strings_to_exc(orths):
    return {orth: [{ORTH: orth}] for orth in orths}


PRON_LEMMA = "-PRON-"


TAG_MAP = {
    "$(":       {TAG: PUNCT, "PunctType": "brck"},
    "$,":       {TAG: PUNCT, "PunctType": "comm"},
    "$.":       {TAG: PUNCT, "PunctType": "peri"},
    "ADJA":     {TAG: ADJ},
    "ADJD":     {TAG: ADJ, "Variant": "short"},
    "ADV":      {TAG: ADV},
    "APPO":     {TAG: ADP, "AdpType": "post"},
    "APPR":     {TAG: ADP, "AdpType": "prep"},
    "APPRART":  {TAG: ADP, "AdpType": "prep", "PronType": "art"},
    "APZR":     {TAG: ADP, "AdpType": "circ"},
    "ART":      {TAG: DET, "PronType": "art"},
    "CARD":     {TAG: NUM, "NumType": "card"},
    "FM":       {TAG: X, "Foreign": "yes"},
    "ITJ":      {TAG: "INTJ"},
    "KOKOM":    {TAG: "CONJ", "ConjType": "comp"},
    "KON":      {TAG: "CONJ"},
    "KOUI":     {TAG: "SCONJ"},
    "KOUS":     {TAG: "SCONJ"},
    "NE":       {TAG: "PROPN"},
    "NNE":      {TAG: "PROPN"},
    "NN":       {TAG: "NOUN"},
    "PAV":      {TAG: ADV, "PronType": "dem"},
    "PROAV":    {TAG: ADV, "PronType": "dem"},
    "PDAT":     {TAG: DET, "PronType": "dem"},
    "PDS":      {TAG: PRON, "PronType": "dem"},
    "PIAT":     {TAG: DET, "PronType": "ind|neg|tot"},
    "PIDAT":    {TAG: DET, "AdjType": "pdt", "PronType": "ind|neg|tot"},
    "PIS":      {TAG: PRON, "PronType": "ind|Neg|tot"},
    "PPER":     {TAG: PRON, "PronType": "prs"},
    "PPOSAT":   {TAG: DET, "Poss": "yes", "PronType": "prs"},
    "PPOSS":    {TAG: PRON, "Poss": "yes", "PronType": "prs"},
    "PRELAT":   {TAG: DET, "PronType": "rel"},
    "PRELS":    {TAG: PRON, "PronType": "rel"},
    "PRF":      {TAG: PRON, "PronType": "prs", "Reflex": "yes"},
    "PTKA":     {TAG: PART},
    "PTKANT":   {TAG: PART, "PartType": "res"},
    "PTKNEG":   {TAG: PART, "Negative": "neg"},
    "PTKVZ":    {TAG: PART, "PartType": "vbp"},
    "PTKZU":    {TAG: PART, "PartType": "inf"},
    "PWAT":     {TAG: DET, "PronType": "int"},
    "PWAV":     {TAG: ADV, "PronType": "int"},
    "PWS":      {TAG: PRON, "PronType": "int"},
    "TRUNC":    {TAG: X, "Hyph": "yes"},
    "VAFIN":    {TAG: AUX, "Mood": "ind", "VerbForm": "fin"},
    "VAIMP":    {TAG: AUX, "Mood": "imp", "VerbForm": "fin"},
    "VAINF":    {TAG: AUX, "VerbForm": "inf"},
    "VAPP":     {TAG: AUX, "Aspect": "perf", "VerbForm": "part"},
    "VMFIN":    {TAG: VERB, "Mood": "ind", "VerbForm": "fin", "VerbType": "mod"},
    "VMINF":    {TAG: VERB, "VerbForm": "inf", "VerbType": "mod"},
    "VMPP":     {TAG: VERB, "Aspect": "perf", "VerbForm": "part", "VerbType": "mod"},
    "VVFIN":    {TAG: VERB, "Mood": "ind", "VerbForm": "fin"},
    "VVIMP":    {TAG: VERB, "Mood": "imp", "VerbForm": "fin"},
    "VVINF":    {TAG: VERB, "VerbForm": "inf"},
    "VVIZU":    {TAG: VERB, "VerbForm": "inf"},
    "VVPP":     {TAG: VERB, "Aspect": "perf", "VerbForm": "part"},
    "XY":       {TAG: X},
    "SP":       {TAG: SPACE}
}


STOP_WORDS = set("""
á a ab aber ach acht achte achten achter achtes ag alle allein allem allen
aller allerdings alles allgemeinen als also am an andere anderen andern anders
auch auf aus ausser außer ausserdem außerdem

bald bei beide beiden beim beispiel bekannt bereits besonders besser besten bin
bis bisher bist

da dabei dadurch dafür dagegen daher dahin dahinter damals damit danach daneben
dank dann daran darauf daraus darf darfst darin darüber darum darunter das
dasein daselbst dass daß dasselbe davon davor dazu dazwischen dein deine deinem
deiner dem dementsprechend demgegenüber demgemäss demgemäß demselben demzufolge
den denen denn denselben der deren derjenige derjenigen dermassen dermaßen
derselbe derselben des deshalb desselben dessen deswegen dich die diejenige
diejenigen dies diese dieselbe dieselben diesem diesen dieser dieses dir doch
dort drei drin dritte dritten dritter drittes du durch durchaus dürfen dürft
durfte durften

eben ebenso ehrlich eigen eigene eigenen eigener eigenes ein einander eine
einem einen einer eines einigeeinigen einiger einiges einmal einmaleins elf en
ende endlich entweder er erst erste ersten erster erstes es etwa etwas euch

früher fünf fünfte fünften fünfter fünftes für

gab ganz ganze ganzen ganzer ganzes gar gedurft gegen gegenüber gehabt gehen
geht gekannt gekonnt gemacht gemocht gemusst genug gerade gern gesagt geschweige
gewesen gewollt geworden gibt ging gleich gott gross groß grosse große grossen
großen grosser großer grosses großes gut gute guter gutes

habe haben habt hast hat hatte hätte hatten hätten heisst heißt her heute hier
hin hinter hoch

ich ihm ihn ihnen ihr ihre ihrem ihrer ihres im immer in indem infolgedessen
ins irgend ist

ja jahr jahre jahren je jede jedem jeden jeder jedermann jedermanns jedoch
jemand jemandem jemanden jene jenem jenen jener jenes jetzt

kam kann kannst kaum kein keine keinem keinen keiner kleine kleinen kleiner
kleines kommen kommt können könnt konnte könnte konnten kurz

lang lange leicht leider lieber los

machen macht machte mag magst man manche manchem manchen mancher manches mehr
mein meine meinem meinen meiner meines mensch menschen mich mir mit mittel
mochte möchte mochten mögen möglich mögt morgen muss muß müssen musst müsst
musste mussten

na nach nachdem nahm natürlich neben nein neue neuen neun neunte neunten neunter
neuntes nicht nichts nie niemand niemandem niemanden noch nun nur

ob oben oder offen oft ohne

recht rechte rechten rechter rechtes richtig rund

sagt sagte sah satt schlecht schon sechs sechste sechsten sechster sechstes
sehr sei seid seien sein seine seinem seinen seiner seines seit seitdem selbst
selbst sich sie sieben siebente siebenten siebenter siebentes siebte siebten
siebter siebtes sind so solang solche solchem solchen solcher solches soll
sollen sollte sollten sondern sonst sowie später statt

tag tage tagen tat teil tel trotzdem tun

über überhaupt übrigens uhr um und uns unser unsere unserer unter

vergangene vergangenen viel viele vielem vielen vielleicht vier vierte vierten
vierter viertes vom von vor

wahr während währenddem währenddessen wann war wäre waren wart warum was wegen
weil weit weiter weitere weiteren weiteres welche welchem welchen welcher
welches wem wen wenig wenige weniger weniges wenigstens wenn wer werde werden
werdet wessen wie wieder will willst wir wird wirklich wirst wo wohl wollen
wollt wollte wollten worden wurde würde wurden würden

zehn zehnte zehnten zehnter zehntes zeit zu zuerst zugleich zum zunächst zur
zurück zusammen zwanzig zwar zwei zweite zweiten zweiter zweites zwischen
""".split())


TOKENIZER_EXCEPTIONS = {
    "\\n": [
        {ORTH: "\\n", LEMMA: "<nl>", TAG: "SP"}
    ],

    "\\t": [
        {ORTH: "\\t", LEMMA: "<tab>", TAG: "SP"}
    ],

    "'S": [
        {ORTH: "'S", LEMMA: PRON_LEMMA}
    ],

    "'n": [
        {ORTH: "'n", LEMMA: "ein"}
    ],

    "'ne": [
        {ORTH: "'ne", LEMMA: "eine"}
    ],

    "'nen": [
        {ORTH: "'nen", LEMMA: "einen"}
    ],

    "'s": [
        {ORTH: "'s", LEMMA: PRON_LEMMA}
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
        {ORTH: "S'", LEMMA: PRON_LEMMA}
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
        {ORTH: "'m", LEMMA: PRON_LEMMA}
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
        {ORTH: "du", LEMMA: PRON_LEMMA},
        {ORTH: "'s", LEMMA: PRON_LEMMA}
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
        {ORTH: "er", LEMMA: PRON_LEMMA},
        {ORTH: "'s", LEMMA: PRON_LEMMA}
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
        {ORTH: "'m", LEMMA: PRON_LEMMA}
    ],

    "i.O.": [
        {ORTH: "i.O.", LEMMA: "in Ordnung"}
    ],

    "i.d.R.": [
        {ORTH: "i.d.R.", LEMMA: "in der Regel"}
    ],

    "ich's": [
        {ORTH: "ich", LEMMA: PRON_LEMMA},
        {ORTH: "'s", LEMMA: PRON_LEMMA}
    ],

    "ihr's": [
        {ORTH: "ihr", LEMMA: PRON_LEMMA},
        {ORTH: "'s", LEMMA: PRON_LEMMA}
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
        {ORTH: "s'", LEMMA: PRON_LEMMA}
    ],

    "s.o.": [
        {ORTH: "s.o.", LEMMA: "siehe oben"}
    ],

    "sie's": [
        {ORTH: "sie", LEMMA: PRON_LEMMA},
        {ORTH: "'s", LEMMA: PRON_LEMMA}
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
        {ORTH: "'m", LEMMA: PRON_LEMMA}
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
        {ORTH: "'m", LEMMA: PRON_LEMMA}
    ],

    "wir's": [
        {ORTH: "wir", LEMMA: PRON_LEMMA},
        {ORTH: "'s", LEMMA: PRON_LEMMA}
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
        {ORTH: "'m", LEMMA: PRON_LEMMA}
    ]
}


ORTH_ONLY = [
    "''",
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
    "z.",
]


TOKENIZER_PREFIXES = r'''
,
"
(
[
{
*
<
>
$
£
„
“
'
``
`
#
US$
C$
A$
a-
‘
....
...
…
‚
»
§
'''.strip().split('\n')


TOKENIZER_SUFFIXES = r'''
,
\"
\)
\]
\}
\*
\!
\?
%
\$
>
:
;
'
”
“
«
_
''
's
'S
’s
’S
’
‘
°
€
…
\.\.
\.\.\.
\.\.\.\.
(?<=[a-zäöüßÖÄÜ)\]"'´«‘’%\)²“”])\.
\-\-
´
(?<=[0-9])km²
(?<=[0-9])m²
(?<=[0-9])cm²
(?<=[0-9])mm²
(?<=[0-9])km³
(?<=[0-9])m³
(?<=[0-9])cm³
(?<=[0-9])mm³
(?<=[0-9])ha
(?<=[0-9])km
(?<=[0-9])m
(?<=[0-9])cm
(?<=[0-9])mm
(?<=[0-9])µm
(?<=[0-9])nm
(?<=[0-9])yd
(?<=[0-9])in
(?<=[0-9])ft
(?<=[0-9])kg
(?<=[0-9])g
(?<=[0-9])mg
(?<=[0-9])µg
(?<=[0-9])t
(?<=[0-9])lb
(?<=[0-9])oz
(?<=[0-9])m/s
(?<=[0-9])km/h
(?<=[0-9])mph
(?<=[0-9])°C
(?<=[0-9])°K
(?<=[0-9])°F
(?<=[0-9])hPa
(?<=[0-9])Pa
(?<=[0-9])mbar
(?<=[0-9])mb
(?<=[0-9])T
(?<=[0-9])G
(?<=[0-9])M
(?<=[0-9])K
(?<=[0-9])kb
'''.strip().split('\n')


TOKENIZER_INFIXES = r'''
…
\.\.\.+
(?<=[a-z])\.(?=[A-Z])
(?<=[a-zöäüßA-ZÖÄÜ"]):(?=[a-zöäüßA-ZÖÄÜ])
(?<=[a-zöäüßA-ZÖÄÜ"])>(?=[a-zöäüßA-ZÖÄÜ])
(?<=[a-zöäüßA-ZÖÄÜ"])<(?=[a-zöäüßA-ZÖÄÜ])
(?<=[a-zöäüßA-ZÖÄÜ"])=(?=[a-zöäüßA-ZÖÄÜ])
'''.strip().split('\n')
