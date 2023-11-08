from ...symbols import NORM, ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

_exc = {}


for exc_data in [
    {ORTH: "jan.", NORM: "januar"},
    {ORTH: "feb.", NORM: "februar"},
    {ORTH: "mar.", NORM: "mars"},
    {ORTH: "apr.", NORM: "april"},
    {ORTH: "jun.", NORM: "juni"},
    {ORTH: "aug.", NORM: "august"},
    {ORTH: "sep.", NORM: "september"},
    {ORTH: "okt.", NORM: "oktober"},
    {ORTH: "nov.", NORM: "november"},
    {ORTH: "des.", NORM: "desember"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


for orth in [
    "Ap.",
    "Aq.",
    "Ca.",
    "Chr.",
    "Co.",
    "Dr.",
    "F.eks.",
    "Fr.p.",
    "Frp.",
    "Grl.",
    "Kr.",
    "Kr.F.",
    "Kr.F.s",
    "Mr.",
    "Mrs.",
    "Pb.",
    "Pr.",
    "Sp.",
    "St.",
    "a.m.",
    "ad.",
    "adm.dir.",
    "adr.",
    "b.c.",
    "bl.a.",
    "bla.",
    "bm.",
    "bnr.",
    "bto.",
    "c.c.",
    "ca.",
    "cand.mag.",
    "co.",
    "d.d.",
    "d.m.",
    "d.y.",
    "dept.",
    "dr.",
    "dr.med.",
    "dr.philos.",
    "dr.psychol.",
    "dss.",
    "dvs.",
    "e.Kr.",
    "e.l.",
    "eg.",
    "eig.",
    "ekskl.",
    "el.",
    "et.",
    "etc.",
    "etg.",
    "ev.",
    "evt.",
    "f.",
    "f.Kr.",
    "f.eks.",
    "f.o.m.",
    "fhv.",
    "fk.",
    "foreg.",
    "fork.",
    "fv.",
    "fvt.",
    "g.",
    "gl.",
    "gno.",
    "gnr.",
    "grl.",
    "gt.",
    "h.r.adv.",
    "hhv.",
    "hoh.",
    "hr.",
    "ifb.",
    "ifm.",
    "iht.",
    "inkl.",
    "istf.",
    "jf.",
    "jr.",
    "jun.",
    "juris.",
    "kfr.",
    "kgl.",
    "kgl.res.",
    "kl.",
    "komm.",
    "kr.",
    "kst.",
    "lat.",
    "lø.",
    "m.a.",
    "m.a.o.",
    "m.fl.",
    "m.m.",
    "m.v.",
    "ma.",
    "mag.art.",
    "md.",
    "mfl.",
    "mht.",
    "mill.",
    "min.",
    "mnd.",
    "moh.",
    "mrd.",
    "muh.",
    "mv.",
    "mva.",
    "n.å.",
    "ndf.",
    "nr.",
    "nto.",
    "nyno.",
    "o.a.",
    "o.l.",
    "obl.",
    "off.",
    "ofl.",
    "on.",
    "op.",
    "org.",
    "osv.",
    "ovf.",
    "p.",
    "p.a.",
    "p.g.a.",
    "p.m.",
    "p.t.",
    "pga.",
    "ph.d.",
    "pkt.",
    "pr.",
    "pst.",
    "pt.",
    "red.anm.",
    "ref.",
    "res.",
    "res.kap.",
    "resp.",
    "rv.",
    "s.",
    "s.d.",
    "s.k.",
    "s.u.",
    "s.å.",
    "sen.",
    "sep.",
    "siviling.",
    "sms.",
    "snr.",
    "spm.",
    "sr.",
    "sst.",
    "st.",
    "st.meld.",
    "st.prp.",
    "stip.",
    "stk.",
    "stud.",
    "sv.",
    "såk.",
    "sø.",
    "t.d.",
    "t.h.",
    "t.o.m.",
    "t.v.",
    "temp.",
    "ti.",
    "tils.",
    "tilsv.",
    "tl;dr",
    "tlf.",
    "to.",
    "ult.",
    "utg.",
    "v.",
    "vedk.",
    "vedr.",
    "vg.",
    "vgs.",
    "vha.",
    "vit.ass.",
    "vn.",
    "vol.",
    "vs.",
    "vsa.",
    "§§",
    "©NTB",
    "årg.",
    "årh.",
]:
    _exc[orth] = [{ORTH: orth}]

# Dates
for h in range(1, 31 + 1):
    for period in ["."]:
        _exc[f"{h}{period}"] = [{ORTH: f"{h}."}]

_custom_base_exc = {"i.": [{ORTH: "i", NORM: "i"}, {ORTH: "."}]}
_exc.update(_custom_base_exc)

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)