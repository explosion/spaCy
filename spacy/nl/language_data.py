# encoding: utf8
from __future__ import unicode_literals
import re

# Stop words are retrieved from http://www.damienvanholten.com/downloads/dutch-stop-words.txt
STOP_WORDS = set("""
aan
af
al
alles
als
altijd
andere
ben
bij
daar
dan
dat
de
der
deze
die
dit
doch
doen
door
dus
een
eens
en
er
ge
geen
geweest
haar
had
heb
hebben
heeft
hem
het
hier
hij
hoe
hun
iemand
iets
ik
in
is
ja
je
kan
kon
kunnen
maar
me
meer
men
met
mij
mijn
moet
na
naar
niet
niets
nog
nu
of
om
omdat
ons
ook
op
over
reeds
te
tegen
toch
toen
tot
u
uit
uw
van
veel
voor
want
waren
was
wat
we
wel
werd
wezen
wie
wij
wil
worden
zal
ze
zei
zelf
zich
zij
zijn
zo
zonder
zou
""".split())


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


TOKENIZER_INFIXES = r'''
\.\.\.
(?<=[a-z])\.(?=[A-Z])
(?<=[a-zöäüßA-ZÖÄÜ"]):(?=[a-zöäüßA-ZÖÄÜ])
(?<=[a-zöäüßA-ZÖÄÜ"])>(?=[a-zöäüßA-ZÖÄÜ])
(?<=[a-zöäüßA-ZÖÄÜ"])<(?=[a-zöäüßA-ZÖÄÜ])
(?<=[a-zöäüßA-ZÖÄÜ"])=(?=[a-zöäüßA-ZÖÄÜ])
'''.strip().split('\n')


#TODO Make tokenizer excpetions for Dutch
TOKENIZER_EXCEPTIONS = {}

#TODO insert TAG_MAP for Dutch
TAG_MAP = {
  "ADV": {
    "pos": "ADV"
  },
  "NOUN": {
    "pos": "NOUN"
  },
  "ADP": {
    "pos": "ADP"
  },
  "PRON": {
    "pos": "PRON"
  },
  "SCONJ": {
    "pos": "SCONJ"
  },
  "PROPN": {
    "pos": "PROPN"
  },
  "DET": {
    "pos": "DET"
  },
  "SYM": {
    "pos": "SYM"
  },
  "INTJ": {
    "pos": "INTJ"
  },
  "PUNCT": {
    "pos": "PUNCT"
  },
  "NUM": {
    "pos": "NUM"
  },
  "AUX": {
    "pos": "AUX"
  },
  "X": {
    "pos": "X"
  },
  "CONJ": {
    "pos": "CONJ"
  },
  "ADJ": {
    "pos": "ADJ"
  },
  "VERB": {
    "pos": "VERB"
  }
}
