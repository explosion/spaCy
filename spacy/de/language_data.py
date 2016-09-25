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


TOKENIZER_INFIXES = r'''
\.\.\.
(?<=[a-z])\.(?=[A-Z])
(?<=[a-zöäüßA-ZÖÄÜ"]):(?=[a-zöäüßA-ZÖÄÜ])
(?<=[a-zöäüßA-ZÖÄÜ"])>(?=[a-zöäüßA-ZÖÄÜ])
(?<=[a-zöäüßA-ZÖÄÜ"])<(?=[a-zöäüßA-ZÖÄÜ])
(?<=[a-zöäüßA-ZÖÄÜ"])=(?=[a-zöäüßA-ZÖÄÜ])
'''.strip().split('\n')


TOKENIZER_EXCEPTIONS = {
    "''": [
        {
            "F": "''"
        }
    ],
    "'S": [
        {
            "F": "'S",
            "L": "es"
        }
    ],
    "'n": [
        {
            "F": "'n",
            "L": "ein"
        }
    ],
    "'ne": [
        {
            "F": "'ne",
            "L": "eine"
        }
    ],
    "'nen": [
        {
            "F": "'nen",
            "L": "einen"
        }
    ],
    "'s": [
        {
            "F": "'s",
            "L": "es"
        }
    ],
    "(:": [
        {
            "F": "(:"
        }
    ],
    "(=": [
        {
            "F": "(="
        }
    ],
    "(^_^)": [
        {
            "F": "(^_^)"
        }
    ],
    "-_-": [
        {
            "F": "-_-"
        }
    ],
    "-__-": [
        {
            "F": "-__-"
        }
    ],
    ":')": [
        {
            "F": ":')"
        }
    ],
    ":(": [
        {
            "F": ":("
        }
    ],
    ":((": [
        {
            "F": ":(("
        }
    ],
    ":(((": [
        {
            "F": ":((("
        }
    ],
    ":)": [
        {
            "F": ":)"
        }
    ],
    ":))": [
        {
            "F": ":))"
        }
    ],
    ":-)": [
        {
            "F": ":-)"
        }
    ],
    ":-/": [
        {
            "F": ":-/"
        }
    ],
    ":-P": [
        {
            "F": ":-P"
        }
    ],
    ":/": [
        {
            "F": ":/"
        }
    ],
    ":0": [
        {
            "F": ":0"
        }
    ],
    ":3": [
        {
            "F": ":3"
        }
    ],
    ":>": [
        {
            "F": ":>"
        }
    ],
    ":O": [
        {
            "F": ":O"
        }
    ],
    ":P": [
        {
            "F": ":P"
        }
    ],
    ":Y": [
        {
            "F": ":Y"
        }
    ],
    ":]": [
        {
            "F": ":]"
        }
    ],
    ":p": [
        {
            "F": ":p"
        }
    ],
    ";(": [
        {
            "F": ";("
        }
    ],
    ";)": [
        {
            "F": ";)"
        }
    ],
    ";-)": [
        {
            "F": ";-)"
        }
    ],
    ";-p": [
        {
            "F": ";-p"
        }
    ],
    ";D": [
        {
            "F": ";D"
        }
    ],
    ";p": [
        {
            "F": ";p"
        }
    ],
    "<3": [
        {
            "F": "<3"
        }
    ],
    "<33": [
        {
            "F": "<33"
        }
    ],
    "<333": [
        {
            "F": "<333"
        }
    ],
    "<space>": [
        {
            "F": "SP"
        }
    ],
    "=)": [
        {
            "F": "=)"
        }
    ],
    "=3": [
        {
            "F": "=3"
        }
    ],
    "=D": [
        {
            "F": "=D"
        }
    ],
    "=[[": [
        {
            "F": "=[["
        }
    ],
    "=]": [
        {
            "F": "=]"
        }
    ],
    "A.C.": [
        {
            "F": "A.C."
        }
    ],
    "A.D.": [
        {
            "F": "A.D."
        }
    ],
    "A.G.": [
        {
            "F": "A.G."
        }
    ],
    "Abb.": [
        {
            "F": "Abb."
        }
    ],
    "Abk.": [
        {
            "F": "Abk."
        }
    ],
    "Abs.": [
        {
            "F": "Abs."
        }
    ],
    "Abt.": [
        {
            "F": "Abt."
        }
    ],
    "Apr.": [
        {
            "F": "Apr."
        }
    ],
    "Aug.": [
        {
            "F": "Aug."
        }
    ],
    "B.A.": [
        {
            "F": "B.A."
        }
    ],
    "B.Sc.": [
        {
            "F": "B.Sc."
        }
    ],
    "Bd.": [
        {
            "F": "Bd."
        }
    ],
    "Betr.": [
        {
            "F": "Betr."
        }
    ],
    "Bf.": [
        {
            "F": "Bf."
        }
    ],
    "Bhf.": [
        {
            "F": "Bhf."
        }
    ],
    "Biol.": [
        {
            "F": "Biol."
        }
    ],
    "Bsp.": [
        {
            "F": "Bsp."
        }
    ],
    "Chr.": [
        {
            "F": "Chr."
        }
    ],
    "Cie.": [
        {
            "F": "Cie."
        }
    ],
    "Co.": [
        {
            "F": "Co."
        }
    ],
    "D.C.": [
        {
            "F": "D.C."
        }
    ],
    "Dez.": [
        {
            "F": "Dez."
        }
    ],
    "Di.": [
        {
            "F": "Di."
        }
    ],
    "Dipl.": [
        {
            "F": "Dipl."
        }
    ],
    "Dipl.-Ing.": [
        {
            "F": "Dipl.-Ing."
        }
    ],
    "Do.": [
        {
            "F": "Do."
        }
    ],
    "Dr.": [
        {
            "F": "Dr."
        }
    ],
    "Fa.": [
        {
            "F": "Fa."
        }
    ],
    "Fam.": [
        {
            "F": "Fam."
        }
    ],
    "Feb.": [
        {
            "F": "Feb."
        }
    ],
    "Fr.": [
        {
            "F": "Fr."
        }
    ],
    "Frl.": [
        {
            "F": "Frl."
        }
    ],
    "G.m.b.H.": [
        {
            "F": "G.m.b.H."
        }
    ],
    "Gebr.": [
        {
            "F": "Gebr."
        }
    ],
    "Hbf.": [
        {
            "F": "Hbf."
        }
    ],
    "Hg.": [
        {
            "F": "Hg."
        }
    ],
    "Hr.": [
        {
            "F": "Hr."
        }
    ],
    "Hrgs.": [
        {
            "F": "Hrgs."
        }
    ],
    "Hrn.": [
        {
            "F": "Hrn."
        }
    ],
    "Hrsg.": [
        {
            "F": "Hrsg."
        }
    ],
    "Ing.": [
        {
            "F": "Ing."
        }
    ],
    "Jan.": [
        {
            "F": "Jan."
        }
    ],
    "Jh.": [
        {
            "F": "Jh."
        }
    ],
    "Jhd.": [
        {
            "F": "Jhd."
        }
    ],
    "Jr.": [
        {
            "F": "Jr."
        }
    ],
    "Jul.": [
        {
            "F": "Jul."
        }
    ],
    "Jun.": [
        {
            "F": "Jun."
        }
    ],
    "K.O.": [
        {
            "F": "K.O."
        }
    ],
    "L.A.": [
        {
            "F": "L.A."
        }
    ],
    "M.A.": [
        {
            "F": "M.A."
        }
    ],
    "M.Sc.": [
        {
            "F": "M.Sc."
        }
    ],
    "Mi.": [
        {
            "F": "Mi."
        }
    ],
    "Mio.": [
        {
            "F": "Mio."
        }
    ],
    "Mo.": [
        {
            "F": "Mo."
        }
    ],
    "Mr.": [
        {
            "F": "Mr."
        }
    ],
    "Mrd.": [
        {
            "F": "Mrd."
        }
    ],
    "Mrz.": [
        {
            "F": "Mrz."
        }
    ],
    "MwSt.": [
        {
            "F": "MwSt."
        }
    ],
    "M\u00e4r.": [
        {
            "F": "M\u00e4r."
        }
    ],
    "N.Y.": [
        {
            "F": "N.Y."
        }
    ],
    "N.Y.C.": [
        {
            "F": "N.Y.C."
        }
    ],
    "Nov.": [
        {
            "F": "Nov."
        }
    ],
    "Nr.": [
        {
            "F": "Nr."
        }
    ],
    "O.K.": [
        {
            "F": "O.K."
        }
    ],
    "Okt.": [
        {
            "F": "Okt."
        }
    ],
    "Orig.": [
        {
            "F": "Orig."
        }
    ],
    "P.S.": [
        {
            "F": "P.S."
        }
    ],
    "Pkt.": [
        {
            "F": "Pkt."
        }
    ],
    "Prof.": [
        {
            "F": "Prof."
        }
    ],
    "R.I.P.": [
        {
            "F": "R.I.P."
        }
    ],
    "Red.": [
        {
            "F": "Red."
        }
    ],
    "S'": [
        {
            "F": "S'",
            "L": "sie"
        }
    ],
    "Sa.": [
        {
            "F": "Sa."
        }
    ],
    "Sep.": [
        {
            "F": "Sep."
        }
    ],
    "Sept.": [
        {
            "F": "Sept."
        }
    ],
    "So.": [
        {
            "F": "So."
        }
    ],
    "St.": [
        {
            "F": "St."
        }
    ],
    "Std.": [
        {
            "F": "Std."
        }
    ],
    "Str.": [
        {
            "F": "Str."
        }
    ],
    "Tel.": [
        {
            "F": "Tel."
        }
    ],
    "Tsd.": [
        {
            "F": "Tsd."
        }
    ],
    "U.S.": [
        {
            "F": "U.S."
        }
    ],
    "U.S.A.": [
        {
            "F": "U.S.A."
        }
    ],
    "U.S.S.": [
        {
            "F": "U.S.S."
        }
    ],
    "Univ.": [
        {
            "F": "Univ."
        }
    ],
    "V_V": [
        {
            "F": "V_V"
        }
    ],
    "Vol.": [
        {
            "F": "Vol."
        }
    ],
    "\\\")": [
        {
            "F": "\\\")"
        }
    ],
    "\\n": [
        {
            "F": "\\n",
            "L": "<nl>",
            "pos": "SP"
        }
    ],
    "\\t": [
        {
            "F": "\\t",
            "L": "<tab>",
            "pos": "SP"
        }
    ],
    "^_^": [
        {
            "F": "^_^"
        }
    ],
    "a.": [
        {
            "F": "a."
        }
    ],
    "a.D.": [
        {
            "F": "a.D."
        }
    ],
    "a.M.": [
        {
            "F": "a.M."
        }
    ],
    "a.Z.": [
        {
            "F": "a.Z."
        }
    ],
    "abzgl.": [
        {
            "F": "abzgl."
        }
    ],
    "adv.": [
        {
            "F": "adv."
        }
    ],
    "al.": [
        {
            "F": "al."
        }
    ],
    "allg.": [
        {
            "F": "allg."
        }
    ],
    "auf'm": [
        {
            "F": "auf",
            "L": "auf"
        },
        {
            "F": "'m",
            "L": "dem"
        }
    ],
    "b.": [
        {
            "F": "b."
        }
    ],
    "betr.": [
        {
            "F": "betr."
        }
    ],
    "biol.": [
        {
            "F": "biol."
        }
    ],
    "bspw.": [
        {
            "F": "bspw."
        }
    ],
    "bzgl.": [
        {
            "F": "bzgl."
        }
    ],
    "bzw.": [
        {
            "F": "bzw."
        }
    ],
    "c.": [
        {
            "F": "c."
        }
    ],
    "ca.": [
        {
            "F": "ca."
        }
    ],
    "co.": [
        {
            "F": "co."
        }
    ],
    "d.": [
        {
            "F": "d."
        }
    ],
    "d.h.": [
        {
            "F": "d.h."
        }
    ],
    "dgl.": [
        {
            "F": "dgl."
        }
    ],
    "du's": [
        {
            "F": "du",
            "L": "du"
        },
        {
            "F": "'s",
            "L": "es"
        }
    ],
    "e.": [
        {
            "F": "e."
        }
    ],
    "e.V.": [
        {
            "F": "e.V."
        }
    ],
    "e.g.": [
        {
            "F": "e.g."
        }
    ],
    "ebd.": [
        {
            "F": "ebd."
        }
    ],
    "ehem.": [
        {
            "F": "ehem."
        }
    ],
    "eigtl.": [
        {
            "F": "eigtl."
        }
    ],
    "engl.": [
        {
            "F": "engl."
        }
    ],
    "entspr.": [
        {
            "F": "entspr."
        }
    ],
    "er's": [
        {
            "F": "er",
            "L": "er"
        },
        {
            "F": "'s",
            "L": "es"
        }
    ],
    "erm.": [
        {
            "F": "erm."
        }
    ],
    "etc.": [
        {
            "F": "etc."
        }
    ],
    "ev.": [
        {
            "F": "ev."
        }
    ],
    "evtl.": [
        {
            "F": "evtl."
        }
    ],
    "f.": [
        {
            "F": "f."
        }
    ],
    "frz.": [
        {
            "F": "frz."
        }
    ],
    "g.": [
        {
            "F": "g."
        }
    ],
    "geb.": [
        {
            "F": "geb."
        }
    ],
    "gegr.": [
        {
            "F": "gegr."
        }
    ],
    "gem.": [
        {
            "F": "gem."
        }
    ],
    "ggf.": [
        {
            "F": "ggf."
        }
    ],
    "ggfs.": [
        {
            "F": "ggfs."
        }
    ],
    "gg\u00fc.": [
        {
            "F": "gg\u00fc."
        }
    ],
    "h.": [
        {
            "F": "h."
        }
    ],
    "h.c.": [
        {
            "F": "h.c."
        }
    ],
    "hinter'm": [
        {
            "F": "hinter",
            "L": "hinter"
        },
        {
            "F": "'m",
            "L": "dem"
        }
    ],
    "hrsg.": [
        {
            "F": "hrsg."
        }
    ],
    "i.": [
        {
            "F": "i."
        }
    ],
    "i.A.": [
        {
            "F": "i.A."
        }
    ],
    "i.G.": [
        {
            "F": "i.G."
        }
    ],
    "i.O.": [
        {
            "F": "i.O."
        }
    ],
    "i.Tr.": [
        {
            "F": "i.Tr."
        }
    ],
    "i.V.": [
        {
            "F": "i.V."
        }
    ],
    "i.d.R.": [
        {
            "F": "i.d.R."
        }
    ],
    "i.e.": [
        {
            "F": "i.e."
        }
    ],
    "ich's": [
        {
            "F": "ich",
            "L": "ich"
        },
        {
            "F": "'s",
            "L": "es"
        }
    ],
    "ihr's": [
        {
            "F": "ihr",
            "L": "ihr"
        },
        {
            "F": "'s",
            "L": "es"
        }
    ],
    "incl.": [
        {
            "F": "incl."
        }
    ],
    "inkl.": [
        {
            "F": "inkl."
        }
    ],
    "insb.": [
        {
            "F": "insb."
        }
    ],
    "j.": [
        {
            "F": "j."
        }
    ],
    "jr.": [
        {
            "F": "jr."
        }
    ],
    "jun.": [
        {
            "F": "jun."
        }
    ],
    "jur.": [
        {
            "F": "jur."
        }
    ],
    "k.": [
        {
            "F": "k."
        }
    ],
    "kath.": [
        {
            "F": "kath."
        }
    ],
    "l.": [
        {
            "F": "l."
        }
    ],
    "lat.": [
        {
            "F": "lat."
        }
    ],
    "lt.": [
        {
            "F": "lt."
        }
    ],
    "m.": [
        {
            "F": "m."
        }
    ],
    "m.E.": [
        {
            "F": "m.E."
        }
    ],
    "m.M.": [
        {
            "F": "m.M."
        }
    ],
    "max.": [
        {
            "F": "max."
        }
    ],
    "min.": [
        {
            "F": "min."
        }
    ],
    "mind.": [
        {
            "F": "mind."
        }
    ],
    "mtl.": [
        {
            "F": "mtl."
        }
    ],
    "n.": [
        {
            "F": "n."
        }
    ],
    "n.Chr.": [
        {
            "F": "n.Chr."
        }
    ],
    "nat.": [
        {
            "F": "nat."
        }
    ],
    "o.": [
        {
            "F": "o."
        }
    ],
    "o.O": [
        {
            "F": "o.O"
        }
    ],
    "o.a.": [
        {
            "F": "o.a."
        }
    ],
    "o.g.": [
        {
            "F": "o.g."
        }
    ],
    "o.k.": [
        {
            "F": "o.k."
        }
    ],
    "o.\u00c4.": [
        {
            "F": "o.\u00c4."
        }
    ],
    "o.\u00e4.": [
        {
            "F": "o.\u00e4."
        }
    ],
    "o_O": [
        {
            "F": "o_O"
        }
    ],
    "o_o": [
        {
            "F": "o_o"
        }
    ],
    "orig.": [
        {
            "F": "orig."
        }
    ],
    "p.": [
        {
            "F": "p."
        }
    ],
    "p.a.": [
        {
            "F": "p.a."
        }
    ],
    "p.s.": [
        {
            "F": "p.s."
        }
    ],
    "pers.": [
        {
            "F": "pers."
        }
    ],
    "phil.": [
        {
            "F": "phil."
        }
    ],
    "q.": [
        {
            "F": "q."
        }
    ],
    "q.e.d.": [
        {
            "F": "q.e.d."
        }
    ],
    "r.": [
        {
            "F": "r."
        }
    ],
    "rer.": [
        {
            "F": "rer."
        }
    ],
    "r\u00f6m.": [
        {
            "F": "r\u00f6m."
        }
    ],
    "s'": [
        {
            "F": "s'",
            "L": "sie"
        }
    ],
    "s.": [
        {
            "F": "s."
        }
    ],
    "s.o.": [
        {
            "F": "s.o."
        }
    ],
    "sen.": [
        {
            "F": "sen."
        }
    ],
    "sie's": [
        {
            "F": "sie",
            "L": "sie"
        },
        {
            "F": "'s",
            "L": "es"
        }
    ],
    "sog.": [
        {
            "F": "sog."
        }
    ],
    "std.": [
        {
            "F": "std."
        }
    ],
    "stellv.": [
        {
            "F": "stellv."
        }
    ],
    "t.": [
        {
            "F": "t."
        }
    ],
    "t\u00e4gl.": [
        {
            "F": "t\u00e4gl."
        }
    ],
    "u.": [
        {
            "F": "u."
        }
    ],
    "u.U.": [
        {
            "F": "u.U."
        }
    ],
    "u.a.": [
        {
            "F": "u.a."
        }
    ],
    "u.s.w.": [
        {
            "F": "u.s.w."
        }
    ],
    "u.v.m.": [
        {
            "F": "u.v.m."
        }
    ],
    "unter'm": [
        {
            "F": "unter",
            "L": "unter"
        },
        {
            "F": "'m",
            "L": "dem"
        }
    ],
    "usf.": [
        {
            "F": "usf."
        }
    ],
    "usw.": [
        {
            "F": "usw."
        }
    ],
    "uvm.": [
        {
            "F": "uvm."
        }
    ],
    "v.": [
        {
            "F": "v."
        }
    ],
    "v.Chr.": [
        {
            "F": "v.Chr."
        }
    ],
    "v.a.": [
        {
            "F": "v.a."
        }
    ],
    "v.l.n.r.": [
        {
            "F": "v.l.n.r."
        }
    ],
    "vgl.": [
        {
            "F": "vgl."
        }
    ],
    "vllt.": [
        {
            "F": "vllt."
        }
    ],
    "vlt.": [
        {
            "F": "vlt."
        }
    ],
    "vor'm": [
        {
            "F": "vor",
            "L": "vor"
        },
        {
            "F": "'m",
            "L": "dem"
        }
    ],
    "vs.": [
        {
            "F": "vs."
        }
    ],
    "w.": [
        {
            "F": "w."
        }
    ],
    "wir's": [
        {
            "F": "wir",
            "L": "wir"
        },
        {
            "F": "'s",
            "L": "es"
        }
    ],
    "wiss.": [
        {
            "F": "wiss."
        }
    ],
    "x.": [
        {
            "F": "x."
        }
    ],
    "xD": [
        {
            "F": "xD"
        }
    ],
    "xDD": [
        {
            "F": "xDD"
        }
    ],
    "y.": [
        {
            "F": "y."
        }
    ],
    "z.": [
        {
            "F": "z."
        }
    ],
    "z.B.": [
        {
            "F": "z.B."
        }
    ],
    "z.Bsp.": [
        {
            "F": "z.Bsp."
        }
    ],
    "z.T.": [
        {
            "F": "z.T."
        }
    ],
    "z.Z.": [
        {
            "F": "z.Z."
        }
    ],
    "z.Zt.": [
        {
            "F": "z.Zt."
        }
    ],
    "z.b.": [
        {
            "F": "z.b."
        }
    ],
    "zzgl.": [
        {
            "F": "zzgl."
        }
    ],
    "\u00e4.": [
        {
            "F": "\u00e4."
        }
    ],
    "\u00f6.": [
        {
            "F": "\u00f6."
        }
    ],
    "\u00f6sterr.": [
        {
            "F": "\u00f6sterr."
        }
    ],
    "\u00fc.": [
        {
            "F": "\u00fc."
        }
    ],
    "\u00fcber'm": [
        {
            "F": "\u00fcber",
            "L": "\u00fcber"
        },
        {
            "F": "'m",
            "L": "dem"
        }
    ]
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
