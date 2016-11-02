# encoding: utf8
from __future__ import unicode_literals
import re


STOP_WORDS = set()


TOKENIZER_PREFIXES = map(re.escape, r'''
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
‚
»
_
§
'''.strip().split('\n'))


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


TOKENIZER_INFIXES = tuple()


TOKENIZER_EXCEPTIONS = {
    "vs.": [{"F": "vs."}],

    "''": [{"F": "''"}],
    "—": [{"F": "—", "L": "--", "pos": "$,"}],

    "a.m.": [{"F": "a.m."}],
    "p.m.": [{"F": "p.m."}],

    "1a.m.": [{"F": "1"}, {"F": "a.m."}],
    "2a.m.": [{"F": "2"}, {"F": "a.m."}],
    "3a.m.": [{"F": "3"}, {"F": "a.m."}],
    "4a.m.": [{"F": "4"}, {"F": "a.m."}],
    "5a.m.": [{"F": "5"}, {"F": "a.m."}],
    "6a.m.": [{"F": "6"}, {"F": "a.m."}],
    "7a.m.": [{"F": "7"}, {"F": "a.m."}],
    "8a.m.": [{"F": "8"}, {"F": "a.m."}],
    "9a.m.": [{"F": "9"}, {"F": "a.m."}],
    "10a.m.": [{"F": "10"}, {"F": "a.m."}],
    "11a.m.": [{"F": "11"}, {"F": "a.m."}],
    "12a.m.": [{"F": "12"}, {"F": "a.m."}],
    "1am": [{"F": "1"}, {"F": "am", "L": "a.m."}],
    "2am": [{"F": "2"}, {"F": "am", "L": "a.m."}],
    "3am": [{"F": "3"}, {"F": "am", "L": "a.m."}],
    "4am": [{"F": "4"}, {"F": "am", "L": "a.m."}],
    "5am": [{"F": "5"}, {"F": "am", "L": "a.m."}],
    "6am": [{"F": "6"}, {"F": "am", "L": "a.m."}],
    "7am": [{"F": "7"}, {"F": "am", "L": "a.m."}],
    "8am": [{"F": "8"}, {"F": "am", "L": "a.m."}],
    "9am": [{"F": "9"}, {"F": "am", "L": "a.m."}],
    "10am": [{"F": "10"}, {"F": "am", "L": "a.m."}],
    "11am": [{"F": "11"}, {"F": "am", "L": "a.m."}],
    "12am": [{"F": "12"}, {"F": "am", "L": "a.m."}],

    "p.m.": [{"F": "p.m."}],
    "1p.m.": [{"F": "1"}, {"F": "p.m."}],
    "2p.m.": [{"F": "2"}, {"F": "p.m."}],
    "3p.m.": [{"F": "3"}, {"F": "p.m."}],
    "4p.m.": [{"F": "4"}, {"F": "p.m."}],
    "5p.m.": [{"F": "5"}, {"F": "p.m."}],
    "6p.m.": [{"F": "6"}, {"F": "p.m."}],
    "7p.m.": [{"F": "7"}, {"F": "p.m."}],
    "8p.m.": [{"F": "8"}, {"F": "p.m."}],
    "9p.m.": [{"F": "9"}, {"F": "p.m."}],
    "10p.m.": [{"F": "10"}, {"F": "p.m."}],
    "11p.m.": [{"F": "11"}, {"F": "p.m."}],
    "12p.m.": [{"F": "12"}, {"F": "p.m."}],
    "1pm": [{"F": "1"}, {"F": "pm", "L": "p.m."}],
    "2pm": [{"F": "2"}, {"F": "pm", "L": "p.m."}],
    "3pm": [{"F": "3"}, {"F": "pm", "L": "p.m."}],
    "4pm": [{"F": "4"}, {"F": "pm", "L": "p.m."}],
    "5pm": [{"F": "5"}, {"F": "pm", "L": "p.m."}],
    "6pm": [{"F": "6"}, {"F": "pm", "L": "p.m."}],
    "7pm": [{"F": "7"}, {"F": "pm", "L": "p.m."}],
    "8pm": [{"F": "8"}, {"F": "pm", "L": "p.m."}],
    "9pm": [{"F": "9"}, {"F": "pm", "L": "p.m."}],
    "10pm": [{"F": "10"}, {"F": "pm", "L": "p.m."}],
    "11pm": [{"F": "11"}, {"F": "pm", "L": "p.m."}],
    "12pm": [{"F": "12"}, {"F": "pm", "L": "p.m."}],

    "Ala.": [{"F": "Ala."}],
    "Ariz.": [{"F": "Ariz."}],
    "Ark.": [{"F":  "Ark."}],
    "Calif.": [{"F": "Calif."}],
    "Colo.": [{"F": "Colo."}],
    "Conn.": [{"F": "Conn."}],
    "Del.": [{"F":  "Del."}],
    "D.C.": [{"F": "D.C."}],
    "Fla.": [{"F":  "Fla."}],
    "Ga.": [{"F": "Ga."}],
    "Ill.": [{"F": "Ill."}],
    "Ind.": [{"F": "Ind."}],
    "Kans.": [{"F": "Kans."}],
    "Kan.": [{"F": "Kan."}],
    "Ky.": [{"F": "Ky."}],
    "La.": [{"F": "La."}],
    "Md.": [{"F": "Md."}],
    "Mass.": [{"F": "Mass."}],
    "Mich.": [{"F": "Mich."}],
    "Minn.": [{"F": "Minn."}],
    "Miss.": [{"F": "Miss."}],
    "Mo.": [{"F": "Mo."}],
    "Mont.": [{"F": "Mont."}],
    "Nebr.": [{"F": "Nebr."}],
    "Neb.": [{"F": "Neb."}],
    "Nev.": [{"F":  "Nev."}],
    "N.H.": [{"F": "N.H."}],
    "N.J.": [{"F": "N.J."}],
    "N.M.": [{"F": "N.M."}],
    "N.Y.": [{"F": "N.Y."}],
    "N.C.": [{"F": "N.C."}],
    "N.D.": [{"F": "N.D."}],
    "Okla.": [{"F": "Okla."}],
    "Ore.": [{"F": "Ore."}],
    "Pa.": [{"F": "Pa."}],
    "Tenn.": [{"F": "Tenn."}],
    "Va.": [{"F": "Va."}],
    "Wash.": [{"F": "Wash."}],
    "Wis.": [{"F": "Wis."}],

    ":)":  [{"F": ":)"}],
    "<3":  [{"F": "<3"}],
    ";)":  [{"F": ";)"}],
    "(:":  [{"F": "(:"}],
    ":(":  [{"F": ":("}],
    "-_-": [{"F": "-_-"}],
    "=)":  [{"F": "=)"}],
    ":/":  [{"F": ":/"}],
    ":>":  [{"F": ":>"}],
    ";-)": [{"F": ";-)"}],
    ":Y":  [{"F": ":Y"}],
    ":P":  [{"F": ":P"}],
    ":-P": [{"F": ":-P"}],
    ":3":  [{"F": ":3"}],
    "=3":  [{"F": "=3"}],
    "xD":  [{"F": "xD"}],
    "^_^": [{"F": "^_^"}],
    "=]":  [{"F": "=]"}],
    "=D":  [{"F": "=D"}],
    "<333":    [{"F": "<333"}],
    ":))": [{"F": ":))"}],
    ":0":  [{"F": ":0"}],
    "-__-":    [{"F": "-__-"}],
    "xDD": [{"F": "xDD"}],
    "o_o": [{"F": "o_o"}],
    "o_O": [{"F": "o_O"}],
    "V_V": [{"F": "V_V"}],
    "=[[": [{"F": "=[["}],
    "<33": [{"F": "<33"}],
    ";p":  [{"F": ";p"}],
    ";D":  [{"F": ";D"}],
    ";-p": [{"F": ";-p"}],
    ";(":  [{"F": ";("}],
    ":p":  [{"F": ":p"}],
    ":]":  [{"F": ":]"}],
    ":O":  [{"F": ":O"}],
    ":-/": [{"F": ":-/"}],
    ":-)": [{"F": ":-)"}],
    ":(((":    [{"F": ":((("}],
    ":((": [{"F": ":(("}],
    ":')": [{"F": ":')"}],
    "(^_^)":   [{"F": "(^_^)"}],
    "(=":  [{"F": "(="}],
    "o.O": [{"F": "o.O"}],
    "\")": [{"F": "\")"}],

    "a.": [{"F": "a."}],
    "b.": [{"F": "b."}],
    "c.": [{"F": "c."}],
    "d.": [{"F": "d."}],
    "e.": [{"F": "e."}],
    "f.": [{"F": "f."}],
    "g.": [{"F": "g."}],
    "h.": [{"F": "h."}],
    "i.": [{"F": "i."}],
    "j.": [{"F": "j."}],
    "k.": [{"F": "k."}],
    "l.": [{"F": "l."}],
    "m.": [{"F": "m."}],
    "n.": [{"F": "n."}],
    "o.": [{"F": "o."}],
    "p.": [{"F": "p."}],
    "q.": [{"F": "q."}],
    "r.": [{"F": "r."}],
    "s.": [{"F": "s."}],
    "t.": [{"F": "t."}],
    "u.": [{"F": "u."}],
    "v.": [{"F": "v."}],
    "w.": [{"F": "w."}],
    "x.": [{"F": "x."}],
    "y.": [{"F": "y."}],
    "z.": [{"F": "z."}],
}


TAG_MAP = {
"$(": {"pos": "PUNCT", "PunctType": "Brck"},
"$,": {"pos": "PUNCT", "PunctType": "Comm"},
"$.": {"pos": "PUNCT", "PunctType": "Peri"},
"ADJA":	{"pos": "ADJ"},
"ADJD":	{"pos": "ADJ", "Variant": "Short"},
"ADV":	{"pos": "ADV"},
"APPO":	{"pos": "ADP", "AdpType": "Post"},
"APPR":	{"pos": "ADP", "AdpType": "Prep"},
"APPRART":	{"pos": "ADP", "AdpType": "Prep", "PronType": "Art"},
"APZR":	{"pos": "ADP", "AdpType": "Circ"},
"ART":	{"pos": "DET", "PronType": "Art"},
"CARD":	{"pos": "NUM", "NumType": "Card"},
"FM":	{"pos": "X", "Foreign": "Yes"},
"ITJ":	{"pos": "INTJ"},
"KOKOM": {"pos": "CONJ", "ConjType": "Comp"},
"KON": {"pos": "CONJ"},
"KOUI":	{"pos": "SCONJ"},
"KOUS":	{"pos": "SCONJ"},
"NE": {"pos": "PROPN"},
"NNE": {"pos": "PROPN"},
"NN": {"pos": "NOUN"},
"PAV": {"pos": "ADV", "PronType": "Dem"},
"PROAV": {"pos": "ADV", "PronType": "Dem"},
"PDAT":	{"pos": "DET", "PronType": "Dem"},
"PDS": {"pos": "PRON", "PronType": "Dem"},
"PIAT":	{"pos": "DET", "PronType": "Ind,Neg,Tot"},
"PIDAT":	{"pos": "DET", "AdjType": "Pdt", "PronType": "Ind,Neg,Tot"},
"PIS":	{"pos": "PRON", "PronType": "Ind,Neg,Tot"},
"PPER":	{"pos": "PRON", "PronType": "Prs"},
"PPOSAT":	{"pos": "DET", "Poss": "Yes", "PronType": "Prs"},
"PPOSS":	{"pos": "PRON", "Poss": "Yes", "PronType": "Prs"},
"PRELAT":	{"pos": "DET", "PronType": "Rel"},
"PRELS":	{"pos": "PRON", "PronType": "Rel"},
"PRF":	{"pos": "PRON", "PronType": "Prs", "Reflex": "Yes"},
"PTKA":	{"pos": "PART"},
"PTKANT":	{"pos": "PART", "PartType": "Res"},
"PTKNEG":	{"pos": "PART", "Negative": "Neg"},
"PTKVZ":	{"pos": "PART", "PartType": "Vbp"},
"PTKZU":	{"pos": "PART", "PartType": "Inf"},
"PWAT":	{"pos": "DET", "PronType": "Int"},
"PWAV":	{"pos": "ADV", "PronType": "Int"},
"PWS":	{"pos": "PRON", "PronType": "Int"},
"TRUNC":	{"pos": "X", "Hyph": "Yes"},
"VAFIN":	{"pos": "AUX", "Mood": "Ind", "VerbForm": "Fin"},
"VAIMP":	{"pos": "AUX", "Mood": "Imp", "VerbForm": "Fin"},
"VAINF":	{"pos": "AUX", "VerbForm": "Inf"},
"VAPP":	{"pos": "AUX", "Aspect": "Perf", "VerbForm": "Part"},
"VMFIN":	{"pos": "VERB", "Mood": "Ind", "VerbForm": "Fin", "VerbType": "Mod"},
"VMINF":	{"pos": "VERB", "VerbForm": "Inf", "VerbType": "Mod"},
"VMPP":	{"pos": "VERB", "Aspect": "Perf", "VerbForm": "Part", "VerbType": "Mod"},
"VVFIN":	{"pos": "VERB", "Mood": "Ind", "VerbForm": "Fin"},
"VVIMP":	{"pos": "VERB", "Mood": "Imp", "VerbForm": "Fin"},
"VVINF":	{"pos": "VERB", "VerbForm": "Inf"},
"VVIZU":	{"pos": "VERB", "VerbForm": "Inf"},
"VVPP":	{"pos": "VERB", "Aspect": "Perf", "VerbForm": "Part"},
"XY":	{"pos": "X"},
"SP": {"pos": "SPACE"}
}
