# encoding: utf8
from __future__ import unicode_literals

import os
import re

import six


def _load_txt_data(*file_paths):
    for path in file_paths:
        with open(path) as f:
            for line in f.readlines():
                if not line.strip().startswith("#"):
                    yield line.strip()


_MODULE_PATH = os.path.dirname(__file__)
_ABBREVIATIONS_ORIG_PATH = _MODULE_PATH + "/data/tokenizer/abbreviations_orig-hu.txt"
_ABBREVIATIONS_NYTUD_PATH = _MODULE_PATH + "/data/tokenizer/abbreviations_nytud-hu.txt"
_STOPWORDS_PATH = _MODULE_PATH + "/data/stopwords.txt"

STOP_WORDS = set(_load_txt_data(_STOPWORDS_PATH))

HYPHENS = [six.unichr(cp) for cp in [173, 8211, 8212, 8213, 8722, 9472]]

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
’
‘
°
€
\.\.
\.\.\.
\.\.\.\.
(?<=[a-züóőúéáűíAÜÓŐÚÉÁŰÍ)\]"'´«‘’%\)²“”])\.
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

TOKENIZER_INFIXES = (r'''\.\.\.+ (?<=[a-z])\.(?=[A-Z]) (?<=[a-zA-Z])-(?=[a-zA-z]) '''
                     r'''(?<=[a-zA-Z])--(?=[a-zA-z]) (?<=[0-9])-(?=[0-9]) '''
                     r'''(?<=[A-Za-z]),(?=[A-Za-z])''').split()

ABBREVIATIONS = {abbrev: [{"F": abbrev}] for abbrev in
                 _load_txt_data(_ABBREVIATIONS_ORIG_PATH, _ABBREVIATIONS_NYTUD_PATH)}

TOKENIZER_EXCEPTIONS = {
    "vs.": [{"F": "vs."}],

    "''": [{"F": "''"}],
    "—": [{"F": "—", "L": "--", "pos": "$,"}],

    ":)": [{"F": ":)"}],
    "<3": [{"F": "<3"}],
    ";)": [{"F": ";)"}],
    "(:": [{"F": "(:"}],
    ":(": [{"F": ":("}],
    "-_-": [{"F": "-_-"}],
    "=)": [{"F": "=)"}],
    ":/": [{"F": ":/"}],
    ":>": [{"F": ":>"}],
    ";-)": [{"F": ";-)"}],
    ":Y": [{"F": ":Y"}],
    ":P": [{"F": ":P"}],
    ":-P": [{"F": ":-P"}],
    ":3": [{"F": ":3"}],
    "=3": [{"F": "=3"}],
    "xD": [{"F": "xD"}],
    "^_^": [{"F": "^_^"}],
    "=]": [{"F": "=]"}],
    "=D": [{"F": "=D"}],
    "<333": [{"F": "<333"}],
    ":))": [{"F": ":))"}],
    ":0": [{"F": ":0"}],
    "-__-": [{"F": "-__-"}],
    "xDD": [{"F": "xDD"}],
    "o_o": [{"F": "o_o"}],
    "o_O": [{"F": "o_O"}],
    "V_V": [{"F": "V_V"}],
    "=[[": [{"F": "=[["}],
    "<33": [{"F": "<33"}],
    ";p": [{"F": ";p"}],
    ";D": [{"F": ";D"}],
    ";-p": [{"F": ";-p"}],
    ";(": [{"F": ";("}],
    ":p": [{"F": ":p"}],
    ":]": [{"F": ":]"}],
    ":O": [{"F": ":O"}],
    ":-/": [{"F": ":-/"}],
    ":-)": [{"F": ":-)"}],
    ":(((": [{"F": ":((("}],
    ":((": [{"F": ":(("}],
    ":')": [{"F": ":')"}],
    "(^_^)": [{"F": "(^_^)"}],
    "(=": [{"F": "(="}],
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

TOKENIZER_EXCEPTIONS.update(ABBREVIATIONS)

TAG_MAP = {
    "$(": {"pos": "PUNCT", "PunctType": "Brck"},
    "$,": {"pos": "PUNCT", "PunctType": "Comm"},
    "$.": {"pos": "PUNCT", "PunctType": "Peri"},
    "ADJA": {"pos": "ADJ"},
    "ADJD": {"pos": "ADJ", "Variant": "Short"},
    "ADV": {"pos": "ADV"},
    "APPO": {"pos": "ADP", "AdpType": "Post"},
    "APPR": {"pos": "ADP", "AdpType": "Prep"},
    "APPRART": {"pos": "ADP", "AdpType": "Prep", "PronType": "Art"},
    "APZR": {"pos": "ADP", "AdpType": "Circ"},
    "ART": {"pos": "DET", "PronType": "Art"},
    "CARD": {"pos": "NUM", "NumType": "Card"},
    "FM": {"pos": "X", "Foreign": "Yes"},
    "ITJ": {"pos": "INTJ"},
    "KOKOM": {"pos": "CONJ", "ConjType": "Comp"},
    "KON": {"pos": "CONJ"},
    "KOUI": {"pos": "SCONJ"},
    "KOUS": {"pos": "SCONJ"},
    "NE": {"pos": "PROPN"},
    "NNE": {"pos": "PROPN"},
    "NN": {"pos": "NOUN"},
    "PAV": {"pos": "ADV", "PronType": "Dem"},
    "PROAV": {"pos": "ADV", "PronType": "Dem"},
    "PDAT": {"pos": "DET", "PronType": "Dem"},
    "PDS": {"pos": "PRON", "PronType": "Dem"},
    "PIAT": {"pos": "DET", "PronType": "Ind,Neg,Tot"},
    "PIDAT": {"pos": "DET", "AdjType": "Pdt", "PronType": "Ind,Neg,Tot"},
    "PIS": {"pos": "PRON", "PronType": "Ind,Neg,Tot"},
    "PPER": {"pos": "PRON", "PronType": "Prs"},
    "PPOSAT": {"pos": "DET", "Poss": "Yes", "PronType": "Prs"},
    "PPOSS": {"pos": "PRON", "Poss": "Yes", "PronType": "Prs"},
    "PRELAT": {"pos": "DET", "PronType": "Rel"},
    "PRELS": {"pos": "PRON", "PronType": "Rel"},
    "PRF": {"pos": "PRON", "PronType": "Prs", "Reflex": "Yes"},
    "PTKA": {"pos": "PART"},
    "PTKANT": {"pos": "PART", "PartType": "Res"},
    "PTKNEG": {"pos": "PART", "Negative": "Neg"},
    "PTKVZ": {"pos": "PART", "PartType": "Vbp"},
    "PTKZU": {"pos": "PART", "PartType": "Inf"},
    "PWAT": {"pos": "DET", "PronType": "Int"},
    "PWAV": {"pos": "ADV", "PronType": "Int"},
    "PWS": {"pos": "PRON", "PronType": "Int"},
    "TRUNC": {"pos": "X", "Hyph": "Yes"},
    "VAFIN": {"pos": "AUX", "Mood": "Ind", "VerbForm": "Fin"},
    "VAIMP": {"pos": "AUX", "Mood": "Imp", "VerbForm": "Fin"},
    "VAINF": {"pos": "AUX", "VerbForm": "Inf"},
    "VAPP": {"pos": "AUX", "Aspect": "Perf", "VerbForm": "Part"},
    "VMFIN": {"pos": "VERB", "Mood": "Ind", "VerbForm": "Fin", "VerbType": "Mod"},
    "VMINF": {"pos": "VERB", "VerbForm": "Inf", "VerbType": "Mod"},
    "VMPP": {"pos": "VERB", "Aspect": "Perf", "VerbForm": "Part", "VerbType": "Mod"},
    "VVFIN": {"pos": "VERB", "Mood": "Ind", "VerbForm": "Fin"},
    "VVIMP": {"pos": "VERB", "Mood": "Imp", "VerbForm": "Fin"},
    "VVINF": {"pos": "VERB", "VerbForm": "Inf"},
    "VVIZU": {"pos": "VERB", "VerbForm": "Inf"},
    "VVPP": {"pos": "VERB", "Aspect": "Perf", "VerbForm": "Part"},
    "XY": {"pos": "X"},
    "SP": {"pos": "SPACE"}
}
