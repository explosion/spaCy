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
    "VNW(pers,pron,nomin,red,3p,ev,masc)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,obl,vol,3,ev,masc)": {
        "pos": "PRON"
    },
    "N(soort,ev,basis,gen)": {
        "pos": "NOUN"
    },
    "WW(pv,tgw,mv)": {
        "pos": "VERB"
    },
    "VNW(pers,pron,obl,vol,2v,ev)": {
        "pos": "PRON"
    },
    "LID(onbep,stan,agr)": {
        "pos": "DET"
    },
    "VNW(pers,pron,stan,nadr,2v,mv)": {
        "pos": "PRON"
    },
    "VNW(onbep,pron,stan,vol,3o,ev)": {
        "pos": "PRON"
    },
    "LID(bep,dial)": {
        "pos": "DET"
    },
    "VNW(pers,pron,nomin,red,1,ev)": {
        "pos": "PRON"
    },
    "WW(inf,nom,zonder,zonder-n)": {
        "pos": "VERB"
    },
    "VNW(pr,pron,obl,vol,1,ev)": {
        "pos": "PRON"
    },
    "SPEC(enof)": {
        "pos": "X"
    },
    "VNW(onbep,det,stan,nom,met-e,mv-n)": {
        "pos": "PRON"
    },
    "VNW(onbep,det,stan,nom,met-e,zonder-n)": {
        "pos": "PRON"
    },
    "VNW(vb,det,stan,prenom,zonder,evon)": {
        "pos": "PRON"
    },
    "VNW(bez,det,stan,vol,1,mv,prenom,zonder,evon)": {
        "pos": "PRON"
    },
    "VNW(onbep,grad,stan,nom,met-e,zonder-n,sup)": {
        "pos": "PRON"
    },
    "TW(hoofd,nom,mv-n,basis)": {
        "pos": "NUM"
    },
    "VNW(onbep,pron,dial)": {
        "pos": "PRON"
    },
    "VNW(aanw,det,stan,nom,met-e,mv-n)": {
        "pos": "PRON"
    },
    "N(soort,ev,dim,onz,stan)": {
        "pos": "NOUN"
    },
    "VNW(aanw,pron,gen,vol,3o,ev)": {
        "pos": "PRON"
    },
    "VNW(bez,det,stan,vol,3,mv,prenom,zonder,agr)": {
        "pos": "PRON"
    },
    "VNW(onbep,grad,stan,vrij,zonder,basis)": {
        "pos": "PRON"
    },
    "VNW(bez,det,stan,vol,1,ev,prenom,zonder,agr)": {
        "pos": "PRON"
    },
    "WW(pv,tgw,ev)": {
        "pos": "VERB"
    },
    "ADJ(vrij,comp,zonder)": {
        "pos": "ADJ"
    },
    "VZ(fin)": {
        "pos": "ADP"
    },
    "VNW(onbep,grad,stan,prenom,met-e,agr,sup)": {
        "pos": "PRON"
    },
    "WW(inf,vrij,zonder)": {
        "pos": "VERB"
    },
    "ADJ(nom,basis,zonder,zonder-n)": {
        "pos": "ADJ"
    },
    "VNW(pers,pron,obl,vol,3,getal,fem)": {
        "pos": "PRON"
    },
    "VNW(refl,pron,obl,red,3,getal)": {
        "pos": "PRON"
    },
    "VNW(onbep,grad,stan,prenom,zonder,agr,comp)": {
        "pos": "PRON"
    },
    "VNW(recip,pron,gen,vol,persoon,mv)": {
        "pos": "PRON"
    },
    "ADJ(prenom,basis,met-e,bijz)": {
        "pos": "ADJ"
    },
    "N(soort,ev,basis,onz,stan)": {
        "pos": "NOUN"
    },
    "VNW(bez,det,stan,vol,3,ev,prenom,zonder,agr)": {
        "pos": "PRON"
    },
    "WW(pv,verl,ev)": {
        "pos": "VERB"
    },
    "TW(rang,prenom,stan)": {
        "pos": "ADJ"
    },
    "VNW(pr,pron,obl,vol,1,mv)": {
        "pos": "PRON"
    },
    "ADJ(nom,sup,zonder,zonder-n)": {
        "pos": "ADJ"
    },
    "VNW(pr,pron,obl,red,1,ev)": {
        "pos": "PRON"
    },
    "VNW(aanw,det,dat,nom,met-e,zonder-n)": {
        "pos": "PRON"
    },
    "WW(pv,conj,ev)": {
        "pos": "VERB"
    },
    "SPEC(afk)": {
        "pos": "X"
    },
    "TW(rang,nom,zonder-n)": {
        "pos": "ADJ"
    },
    "VNW(onbep,det,gen,prenom,met-e,mv)": {
        "pos": "PRON"
    },
    "VNW(vb,pron,gen,vol,3p,mv)": {
        "pos": "PRON"
    },
    "VNW(betr,pron,stan,vol,3,ev)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,nomin,red,1,mv)": {
        "pos": "PRON"
    },
    "VNW(vb,pron,stan,vol,3o,ev)": {
        "pos": "PRON"
    },
    "WW(pv,verl,mv)": {
        "pos": "VERB"
    },
    "TW(hoofd,prenom,stan)": {
        "pos": "NUM"
    },
    "VNW(aanw,det,stan,prenom,met-e,rest)": {
        "pos": "PRON"
    },
    "VNW(vb,det,stan,prenom,met-e,rest)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,nomin,vol,3p,mv)": {
        "pos": "PRON"
    },
    "VNW(pr,pron,obl,vol,2,getal)": {
        "pos": "PRON"
    },
    "ADJ(prenom,basis,zonder)": {
        "pos": "ADJ"
    },
    "TSW()": {
        "pos": "INTJ"
    },
    "VNW(betr,det,stan,nom,zonder,zonder-n)": {
        "pos": "PRON"
    },
    "VZ(init)": {
        "pos": "ADP"
    },
    "VNW(pers,pron,nomin,nadr,3v,ev,fem)": {
        "pos": "PRON"
    },
    "ADJ(vrij,dim,zonder)": {
        "pos": "ADJ"
    },
    "TW(hoofd,dial)": {
        "pos": "NUM"
    },
    "VNW(onbep,grad,stan,prenom,met-e,agr,basis)": {
        "pos": "PRON"
    },
    "TW(hoofd,nom,zonder-n,dim)": {
        "pos": "NUM"
    },
    "ADJ(prenom,comp,zonder)": {
        "pos": "ADJ"
    },
    "WW(od,prenom,met-e)": {
        "pos": "VERB"
    },
    "VNW(bez,det,dial)": {
        "pos": "PRON"
    },
    "VNW(bez,det,stan,red,3,ev,prenom,zonder,agr)": {
        "pos": "PRON"
    },
    "VNW(aanw,det,stan,prenom,zonder,agr)": {
        "pos": "PRON"
    },
    "N(soort,mv,basis)": {
        "pos": "NOUN"
    },
    "VNW(onbep,pron,gen,vol,3p,ev)": {
        "pos": "PRON"
    },
    "LID(onbep,dial)": {
        "pos": "DET"
    },
    "VNW(bez,det,stan,vol,2v,ev,prenom,zonder,agr)": {
        "pos": "PRON"
    },
    "N(soort,ev,basis,genus,stan)": {
        "pos": "NOUN"
    },
    "VNW(aanw,det,dial)": {
        "pos": "PRON"
    },
    "N(soort,ev,basis,dat)": {
        "pos": "NOUN"
    },
    "VNW(onbep,det,stan,prenom,zonder,agr)": {
        "pos": "PRON"
    },
    "LID(bep,gen,rest3)": {
        "pos": "DET"
    },
    "TSW(dial)": {
        "pos": "INTJ"
    },
    "ADJ(nom,basis,met-e,mv-n)": {
        "pos": "ADJ"
    },
    "VNW(onbep,grad,stan,prenom,met-e,mv,basis)": {
        "pos": "PRON"
    },
    "BW(dial)": {
        "pos": "ADV"
    },
    "ADJ(nom,comp,met-e,mv-n)": {
        "pos": "ADJ"
    },
    "LID(bep,stan,evon)": {
        "pos": "DET"
    },
    "WW(vd,nom,met-e,mv-n)": {
        "pos": "VERB"
    },
    "VNW(onbep,grad,stan,nom,zonder,zonder-n,sup)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,obl,nadr,3p,mv)": {
        "pos": "PRON"
    },
    "WW(vd,prenom,met-e)": {
        "pos": "VERB"
    },
    "VNW(bez,det,stan,vol,3m,ev,prenom,met-e,rest)": {
        "pos": "PRON"
    },
    "VG(neven)": {
        "pos": "CONJ"
    },
    "VNW(pers,pron,nomin,vol,2b,getal)": {
        "pos": "PRON"
    },
    "WW(pv,verl,met-t)": {
        "pos": "VERB"
    },
    "VNW(recip,pron,obl,vol,persoon,mv)": {
        "pos": "PRON"
    },
    "ADJ(prenom,comp,met-e,stan)": {
        "pos": "ADJ"
    },
    "VNW(onbep,grad,stan,prenom,met-e,agr,comp)": {
        "pos": "PRON"
    },
    "ADJ(nom,comp,met-e,zonder-n,stan)": {
        "pos": "ADJ"
    },
    "SPEC(deeleigen)": {
        "pos": "X"
    },
    "VNW(vb,pron,stan,vol,3p,getal)": {
        "pos": "PRON"
    },
    "ADJ(postnom,basis,zonder)": {
        "pos": "ADJ"
    },
    "WW(od,nom,met-e,zonder-n)": {
        "pos": "VERB"
    },
    "VNW(vrag,pron,dial)": {
        "pos": "PRON"
    },
    "VNW(onbep,grad,stan,nom,met-e,zonder-n,basis)": {
        "pos": "PRON"
    },
    "VNW(bez,det,stan,vol,2,getal,prenom,zonder,agr)": {
        "pos": "PRON"
    },
    "VNW(onbep,det,dial)": {
        "pos": "PRON"
    },
    "TW(rang,dial)": {
        "pos": "ADJ"
    },
    "VNW(onbep,det,stan,prenom,zonder,evon)": {
        "pos": "PRON"
    },
    "N(soort,dial)": {
        "pos": "NOUN"
    },
    "VNW(excl,pron,stan,vol,3,getal)": {
        "pos": "PRON"
    },
    "WW(vd,vrij,zonder)": {
        "pos": "VERB"
    },
    "SPEC(vreemd)": {
        "pos": "X"
    },
    "VNW(aanw,adv-pron,stan,red,3,getal)": {
        "pos": "PRON"
    },
    "WW(vd,nom,met-e,zonder-n)": {
        "pos": "VERB"
    },
    "VNW(aanw,adv-pron,obl,vol,3o,getal)": {
        "pos": "PRON"
    },
    "VNW(aanw,det,stan,nom,met-e,zonder-n)": {
        "pos": "PRON"
    },
    "ADJ(dial)": {
        "pos": "ADJ"
    },
    "ADJ(vrij,sup,zonder)": {
        "pos": "ADJ"
    },
    "ADJ(nom,sup,met-e,mv-n)": {
        "pos": "ADJ"
    },
    "LID(bep,gen,evmo)": {
        "pos": "DET"
    },
    "VNW(onbep,grad,stan,nom,met-e,mv-n,basis)": {
        "pos": "PRON"
    },
    "VG(onder,dial)": {
        "pos": "SCONJ"
    },
    "ADJ(vrij,basis,zonder)": {
        "pos": "ADJ"
    },
    "ADJ(postnom,basis,met-s)": {
        "pos": "ADJ"
    },
    "VNW(aanw,pron,stan,vol,3,getal)": {
        "pos": "PRON"
    },
    "VG(onder)": {
        "pos": "SCONJ"
    },
    "WW(od,prenom,zonder)": {
        "pos": "VERB"
    },
    "VNW(pers,pron,nomin,red,3,ev,masc)": {
        "pos": "PRON"
    },
    "VNW(onbep,grad,stan,vrij,zonder,comp)": {
        "pos": "PRON"
    },
    "VNW(betr,pron,gen,vol,3o,getal)": {
        "pos": "PRON"
    },
    "VNW(aanw,det,stan,vrij,zonder)": {
        "pos": "PRON"
    },
    "LET()": {
        "pos": "PUNCT"
    },
    "VNW(pers,pron,nomin,vol,1,ev)": {
        "pos": "PRON"
    },
    "VNW(refl,pron,obl,nadr,3,getal)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,nomin,red,2,getal)": {
        "pos": "PRON"
    },
    "N(soort,mv,dim)": {
        "pos": "NOUN"
    },
    "VNW(pers,pron,stan,red,3,ev,fem)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,obl,nadr,3m,ev,masc)": {
        "pos": "PRON"
    },
    "VNW(onbep,adv-pron,obl,vol,3o,getal)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,nomin,vol,2v,ev)": {
        "pos": "PRON"
    },
    "ADJ(nom,basis,met-e,zonder-n,stan)": {
        "pos": "ADJ"
    },
    "SPEC(symb)": {
        "pos": "X"
    },
    "VNW(aanw,pron,gen,vol,3m,ev)": {
        "pos": "PRON"
    },
    "VNW(refl,pron,dial)": {
        "pos": "PRON"
    },
    "VNW(onbep,det,stan,prenom,met-e,evz)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,obl,red,3,ev,masc)": {
        "pos": "PRON"
    },
    "VNW(onbep,det,stan,nom,zonder,zonder-n)": {
        "pos": "PRON"
    },
    "VNW(onbep,det,stan,prenom,met-e,rest)": {
        "pos": "PRON"
    },
    "VNW(onbep,det,stan,prenom,met-e,mv)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,nomin,red,2v,ev)": {
        "pos": "PRON"
    },
    "ADJ(prenom,basis,met-e,stan)": {
        "pos": "ADJ"
    },
    "VNW(bez,det,stan,red,1,ev,prenom,zonder,agr)": {
        "pos": "PRON"
    },
    "SPEC(afgebr)": {
        "pos": "X"
    },
    "VNW(onbep,pron,stan,vol,3p,ev)": {
        "pos": "PRON"
    },
    "VNW(onbep,grad,stan,nom,met-e,mv-n,sup)": {
        "pos": "PRON"
    },
    "VNW(onbep,det,stan,prenom,met-e,agr)": {
        "pos": "PRON"
    },
    "WW(pv,tgw,met-t)": {
        "pos": "VERB"
    },
    "VNW(aanw,det,stan,prenom,zonder,rest)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,stan,red,3,ev,onz)": {
        "pos": "PRON"
    },
    "WW(vd,prenom,zonder)": {
        "pos": "VERB"
    },
    "VNW(pers,pron,nomin,vol,1,mv)": {
        "pos": "PRON"
    },
    "WW(od,nom,met-e,mv-n)": {
        "pos": "VERB"
    },
    "VNW(aanw,pron,stan,vol,3o,ev)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,dial)": {
        "pos": "PRON"
    },
    "VNW(pr,pron,obl,red,2v,getal)": {
        "pos": "PRON"
    },
    "ADJ(nom,basis,zonder,mv-n)": {
        "pos": "ADJ"
    },
    "VNW(onbep,det,stan,vrij,zonder)": {
        "pos": "PRON"
    },
    "LID(bep,stan,rest)": {
        "pos": "DET"
    },
    "VNW(pers,pron,nomin,vol,3v,ev,fem)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,nomin,vol,3,ev,masc)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,stan,red,3,mv)": {
        "pos": "PRON"
    },
    "VNW(bez,det,stan,nadr,2v,mv,prenom,zonder,agr)": {
        "pos": "PRON"
    },
    "ADJ(nom,sup,met-e,zonder-n,stan)": {
        "pos": "ADJ"
    },
    "VNW(pers,pron,obl,vol,3p,mv)": {
        "pos": "PRON"
    },
    "VNW(bez,det,stan,vol,1,mv,prenom,met-e,rest)": {
        "pos": "PRON"
    },
    "VNW(onbep,grad,stan,vrij,zonder,sup)": {
        "pos": "PRON"
    },
    "VNW(bez,det,stan,red,2v,ev,prenom,zonder,agr)": {
        "pos": "PRON"
    },
    "TW(hoofd,vrij)": {
        "pos": "NUM"
    },
    "VNW(onbep,grad,stan,prenom,zonder,agr,basis)": {
        "pos": "PRON"
    },
    "VNW(aanw,det,stan,prenom,zonder,evon)": {
        "pos": "PRON"
    },
    "VNW(onbep,adv-pron,gen,red,3,getal)": {
        "pos": "PRON"
    },
    "VNW(pers,pron,nomin,vol,2,getal)": {
        "pos": "PRON"
    },
    "VNW(pr,pron,obl,nadr,1,ev)": {
        "pos": "PRON"
    },
    "VNW(pr,pron,obl,nadr,2v,getal)": {
        "pos": "PRON"
    },
    "VNW(vb,det,stan,nom,met-e,zonder-n)": {
        "pos": "PRON"
    },
    "VNW(betr,pron,stan,vol,persoon,getal)": {
        "pos": "PRON"
    },
    "TW(hoofd,nom,zonder-n,basis)": {
        "pos": "NUM"
    },
    "VNW(vb,pron,gen,vol,3m,ev)": {
        "pos": "PRON"
    },
    "WW(inf,prenom,zonder)": {
        "pos": "VERB"
    },
    "TW(rang,nom,mv-n)": {
        "pos": "ADJ"
    },
    "SPEC(meta)": {
        "pos": "X"
    },
    "LID(bep,dat,evmo)": {
        "pos": "DET"
    },
    "N(soort,ev,basis,zijd,stan)": {
        "pos": "NOUN"
    },
    "VNW(pers,pron,nomin,nadr,3m,ev,masc)": {
        "pos": "PRON"
    },
    "WW(od,vrij,zonder)": {
        "pos": "VERB"
    },
    "VNW(vb,adv-pron,obl,vol,3o,getal)": {
        "pos": "PRON"
    },
    "ADJ(prenom,sup,zonder)": {
        "pos": "ADJ"
    },
    "BW()": {
        "pos": "ADV"
    },
    "VZ(versm)": {
        "pos": "ADP"
    },
    "ADJ(prenom,sup,met-e,stan)": {
        "pos": "ADJ"
    }
}
