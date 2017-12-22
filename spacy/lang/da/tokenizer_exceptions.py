# encoding: utf8
"""
Tokenizer Exceptions.
Source: https://forkortelse.dk/ and various others.
"""

from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM, TAG, PUNCT


_exc = {}

# Abbreviations for weekdays "søn." (for "søndag") as well as "Tor." and "Tors."
# (for "torsdag") are left out because they are ambiguous. The same is the case
# for abbreviations "jul." and "Jul." ("juli").
for exc_data in [
        {ORTH: "Kbh.", LEMMA: "København", NORM: "København"},
        {ORTH: "jan.", LEMMA: "januar"},
        {ORTH: "febr.", LEMMA: "februar"},
        {ORTH: "feb.", LEMMA: "februar"},
        {ORTH: "mar.", LEMMA: "marts"},
        {ORTH: "apr.", LEMMA: "april"},
        {ORTH: "jun.", LEMMA: "juni"},
        {ORTH: "aug.", LEMMA: "august"},
        {ORTH: "sept.", LEMMA: "september"},
        {ORTH: "sep.", LEMMA: "september"},
        {ORTH: "okt.", LEMMA: "oktober"},
        {ORTH: "nov.", LEMMA: "november"},
        {ORTH: "dec.", LEMMA: "december"},
        {ORTH: "man.", LEMMA: "mandag"},
        {ORTH: "tirs.", LEMMA: "tirsdag"},
        {ORTH: "ons.", LEMMA: "onsdag"},
        {ORTH: "tor.", LEMMA: "torsdag"},
        {ORTH: "tors.", LEMMA: "torsdag"},
        {ORTH: "fre.", LEMMA: "fredag"},
        {ORTH: "lør.", LEMMA: "lørdag"},
        {ORTH: "Jan.", LEMMA: "januar"},
        {ORTH: "Febr.", LEMMA: "februar"},
        {ORTH: "Feb.", LEMMA: "februar"},
        {ORTH: "Mar.", LEMMA: "marts"},
        {ORTH: "Apr.", LEMMA: "april"},
        {ORTH: "Jun.", LEMMA: "juni"},
        {ORTH: "Aug.", LEMMA: "august"},
        {ORTH: "Sept.", LEMMA: "september"},
        {ORTH: "Sep.", LEMMA: "september"},
        {ORTH: "Okt.", LEMMA: "oktober"},
        {ORTH: "Nov.", LEMMA: "november"},
        {ORTH: "Dec.", LEMMA: "december"},
        {ORTH: "Man.", LEMMA: "mandag"},
        {ORTH: "Tirs.", LEMMA: "tirsdag"},
        {ORTH: "Ons.", LEMMA: "onsdag"},
        {ORTH: "Fre.", LEMMA: "fredag"},
        {ORTH: "Lør.", LEMMA: "lørdag"}]:
    _exc[exc_data[ORTH]] = [exc_data]


# Specified case only
for orth in [
        "diam.", "ib.", "mia.", "mik.", "pers.", "A.D.", "A/S", "B.C.", "BK.",
        "Dr.", "Boul.", "Chr.", "Dronn.", "H.K.H.", "H.M.", "Hf.", "i/s", "I/S",
        "Kprs.", "L.A.", "Ll.", "m/s", "M/S", "Mag.", "Mr.", "Ndr.", "Ph.d.",
        "Prs.", "Rcp.", "Sdr.", "Skt.", "Spl.", "Vg."]:
    _exc[orth] = [{ORTH: orth}]


for orth in [
        "aarh.", "ac.", "adj.", "adr.", "adsk.", "adv.", "afb.", "afd.", "afg.",
        "afk.", "afs.", "aht.", "alg.", "alk.", "alm.", "amer.", "ang.", "ank.",
        "anl.", "anv.", "arb.", "arr.", "att.", "bd.", "bdt.", "beg.", "begr.",
        "beh.", "bet.", "bev.", "bhk.", "bib.", "bibl.", "bidr.", "bildl.",
        "bill.", "biol.", "bk.", "bl.", "bl.a.", "borgm.", "br.", "brolægn.",
        "bto.", "bygn.", "ca.", "cand.", "d.d.", "d.m.", "d.s.", "d.s.s.",
        "d.y.", "d.å.", "d.æ.", "dagl.", "dat.", "dav.", "def.", "dek.", "dep.",
        "desl.", "dir.", "disp.", "distr.", "div.", "dkr.", "dl.", "do.",
        "dobb.", "dr.h.c", "dr.phil.", "ds.", "dvs.", "e.b.", "e.l.", "e.o.",
        "e.v.t.", "eftf.", "eftm.", "egl.", "eks.", "eksam.", "ekskl.", "eksp.",
        "ekspl.", "el.lign.", "emer.", "endv.", "eng.", "enk.", "etc.", "etym.",
        "eur.", "evt.", "exam.", "f.eks.", "f.m.", "f.n.", "f.o.", "f.o.m.",
        "f.s.v.", "f.t.", "f.v.t.", "f.å.", "fa.", "fakt.", "fam.", "ff.",
        "fg.", "fhv.", "fig.", "filol.", "filos.", "fl.", "flg.", "fm.", "fmd.",
        "fol.", "forb.", "foreg.", "foren.", "forf.", "fork.", "forr.", "fors.",
        "forsk.", "forts.", "fr.", "fr.u.", "frk.", "fsva.", "fuldm.", "fung.",
        "fx.", "fys.", "fær.", "g.d.", "g.m.", "gd.", "gdr.", "genuds.", "gl.",
        "gn.", "gns.", "gr.", "grdl.", "gross.", "h.a.", "h.c.", "hdl.",
        "henv.", "hhv.", "hj.hj.", "hj.spl.", "hort.", "hosp.", "hpl.", "hr.",
        "hrs.", "hum.", "hvp.", "i.e.", "id.", "if.", "iflg.", "ifm.", "ift.",
        "iht.", "ill.", "indb.", "indreg.", "inf.", "ing.", "inh.", "inj.",
        "inkl.", "insp.", "instr.", "isl.", "istf.", "it.", "ital.", "iv.",
        "jap.", "jf.", "jfr.", "jnr.", "j.nr.", "jr.", "jur.", "jvf.", "kap.",
        "kbh.", "kem.", "kgl.", "kl.", "kld.", "knsp.", "komm.", "kons.",
        "korr.", "kp.", "kr.", "kst.", "kt.", "ktr.", "kv.", "kvt.", "l.c.",
        "lab.", "lat.", "lb.m.", "lb.nr.", "lejl.", "lgd.", "lic.", "lign.",
        "lin.", "ling.merc.", "litt.", "loc.cit.", "lok.", "lrs.", "ltr.",
        "m.a.o.", "m.fl.", "m.m.", "m.v.", "m.v.h.", "maks.", "md.", "mdr.",
        "mdtl.", "mezz.", "mfl.", "m.h.p.", "m.h.t.", "mht.", "mill.", "mio.",
        "modt.", "mrk.", "mul.", "mv.", "n.br.", "n.f.", "nb.", "nedenst.",
        "nl.", "nr.", "nto.", "nuv.", "o/m", "o.a.", "o.fl.", "o.h.", "o.l.",
        "o.lign.", "o.m.a.", "o.s.fr.", "obl.", "obs.", "odont.", "oecon.",
        "off.", "ofl.", "omg.", "omkr.", "omr.", "omtr.", "opg.", "opl.",
        "opr.", "org.", "orig.", "osv.", "ovenst.", "overs.", "ovf.", "p.a.",
        "p.b.a", "p.b.v", "p.c.", "p.m.", "p.m.v.", "p.n.", "p.p.", "p.p.s.",
        "p.s.", "p.t.", "p.v.a.", "p.v.c.", "pag.", "pass.", "pcs.", "pct.",
        "pd.", "pens.", "pft.", "pg.", "pga.", "pgl.", "pinx.", "pk.", "pkt.",
        "polit.", "polyt.", "pos.", "pp.", "ppm.", "pr.", "prc.", "priv.",
        "prod.", "prof.", "pron.", "præd.", "præf.", "præt.", "psych.", "pt.",
        "pæd.", "q.e.d.", "rad.", "red.", "ref.", "reg.", "regn.", "rel.",
        "rep.", "repr.", "resp.", "rest.", "rm.", "rtg.", "russ.", "s.br.",
        "s.d.", "s.f.", "s.m.b.a.", "s.u.", "s.å.", "sa.", "sb.", "sc.",
        "scient.", "scil.", "sek.", "sekr.", "self.", "sem.", "shj.", "sign.",
        "sing.", "sj.", "skr.", "slutn.", "sml.", "smp.", "snr.", "soc.",
        "soc.dem.", "sp.", "spec.", "spm.", "spr.", "spsk.", "statsaut.", "st.",
        "stk.", "str.", "stud.", "subj.", "subst.", "suff.", "sup.", "suppl.",
        "sv.", "såk.", "sædv.", "t/r", "t.h.", "t.o.", "t.o.m.", "t.v.", "tbl.",
        "tcp/ip", "td.", "tdl.", "tdr.", "techn.", "tekn.", "temp.", "th.",
        "theol.", "tidl.", "tilf.", "tilh.", "till.", "tilsv.", "tjg.", "tkr.",
        "tlf.", "tlgr.", "tr.", "trp.", "tsk.", "tv.", "ty.", "u/b", "udb.",
        "udbet.", "ugtl.", "undt.", "v.f.", "vb.", "vedk.", "vedl.", "vedr.",
        "vejl.", "vh.", "vha.", "vs.", "vsa.", "vær.", "zool.", "ø.lgd.",
        "øvr.", "årg.", "årh."]:
    _exc[orth] = [{ORTH: orth}]
    capitalized = orth.capitalize()
    _exc[capitalized] = [{ORTH: capitalized}]

for exc_data in [
        {ORTH: "s'gu", LEMMA: "s'gu", NORM: "s'gu"},
        {ORTH: "S'gu", LEMMA: "s'gu", NORM: "s'gu"},
        {ORTH: "sgu'", LEMMA: "s'gu", NORM: "s'gu"},
        {ORTH: "Sgu'", LEMMA: "s'gu", NORM: "s'gu"},
        {ORTH: "sku'", LEMMA: "skal", NORM: "skulle"},
        {ORTH: "ku'", LEMMA: "kan", NORM: "kunne"},
        {ORTH: "Ku'", LEMMA: "kan", NORM: "kunne"},
        {ORTH: "ka'", LEMMA: "kan", NORM: "kan"},
        {ORTH: "Ka'", LEMMA: "kan", NORM: "kan"},
        {ORTH: "gi'", LEMMA: "give", NORM: "giv"},
        {ORTH: "Gi'", LEMMA: "give", NORM: "giv"},
        {ORTH: "li'", LEMMA: "lide", NORM: "lide"},
        {ORTH: "ha'", LEMMA: "have", NORM: "have"},
        {ORTH: "Ha'", LEMMA: "have", NORM: "have"},
        {ORTH: "ik'", LEMMA: "ikke", NORM: "ikke"},
        {ORTH: "Ik'", LEMMA: "ikke", NORM: "ikke"}]:
    _exc[exc_data[ORTH]] = [exc_data]


# Dates
for h in range(1, 31 + 1):
    for period in ["."]:
        _exc["%d%s" % (h, period)] = [{ORTH: "%d." % h}]

_custom_base_exc = {
    "i.": [
        {ORTH: "i", LEMMA: "i", NORM: "i"},
        {ORTH: ".", TAG: PUNCT}]
}
_exc.update(_custom_base_exc)

TOKENIZER_EXCEPTIONS = _exc
