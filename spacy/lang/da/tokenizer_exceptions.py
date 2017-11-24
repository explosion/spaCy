# encoding: utf8
"""
Tokenizer Exceptions.
Source: https://forkortelse.dk/ and various others.
"""

from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM, TAG, ADP, PUNCT


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

for orth in [
        "A.D.", "A/S", "aarh.", "ac.", "adj.", "adr.", "adsk.", "adv.", "afb.",
        "afd.", "afg.", "afk.", "afs.", "aht.", "alg.", "alk.", "alm.", "amer.",
        "ang.", "ank.", "anl.", "anv.", "arb.", "arr.", "att.", "B.C.", "bd.",
        "bdt.", "beg.", "begr.", "beh.", "bet.", "bev.", "bhk.", "bib.",
        "bibl.", "bidr.", "bildl.", "bill.", "bio.", "biol.", "bk.", "BK.",
        "bl.", "bl.a.", "borgm.", "bot.", "Boul.", "br.", "brolægn.", "bto.",
        "bygn.", "ca.", "cand.", "Chr.", "d.", "d.d.", "d.m.", "d.s.", "d.s.s.",
        "d.y.", "d.å.", "d.æ.", "da.", "dagl.", "dat.", "dav.", "def.", "dek.",
        "dep.", "desl.", "diam.", "dir.", "disp.", "distr.", "div.", "dkr.",
        "dl.", "do.", "dobb.", "Dr.", "dr.h.c", "Dronn.", "ds.", "dvs.", "e.b.",
        "e.l.", "e.o.", "e.v.t.", "eftf.", "eftm.", "eg.", "egl.", "eks.",
        "eksam.", "ekskl.", "eksp.", "ekspl.", "el.", "el.lign.", "emer.",
        "endv.", "eng.", "enk.", "etc.", "etym.", "eur.", "evt.", "exam.", "f.",
        "f.eks.", "f.m.", "f.n.", "f.o.", "f.o.m.", "f.s.v.", "f.t.", "f.v.t.",
        "f.å.", "fa.", "fakt.", "fam.", "fem.", "ff.", "fg.", "fhv.", "fig.",
        "filol.", "filos.", "fl.", "flg.", "fm.", "fmd.", "fol.", "forb.",
        "foreg.", "foren.", "forf.", "fork.", "form.", "forr.", "fors.",
        "forsk.", "forts.", "fr.", "fr.u.", "frk.", "fsva.", "fuldm.", "fung.",
        "fx.", "fys.", "fær.", "g.d.", "g.m.", "gd.", "gdr.", "genuds.", "gl.",
        "gn.", "gns.", "gr.", "grdl.", "gross.", "h.a.", "h.c.", "H.K.H.",
        "H.M.", "hdl.", "henv.", "Hf.", "hhv.", "hj.hj.", "hj.spl.", "hort.",
        "hosp.", "hpl.", "Hr.", "hr.", "hrs.", "hum.", "hvp.", "i/s", "I/S",
        "i.e.", "ib.", "id.", "if.", "iflg.", "ifm.", "ift.", "iht.", "ill.",
        "indb.", "indreg.", "inf.", "ing.", "inh.", "inj.", "inkl.", "insp.",
        "instr.", "isl.", "istf.", "it.", "ital.", "iv.", "jap.", "jf.", "jfr.",
        "jnr.", "j.nr.", "jr.", "jur.", "jvf.", "K.", "kap.", "kat.", "kbh.",
        "kem.", "kgl.", "kl.", "kld.", "knsp.", "komm.", "kons.", "korr.",
        "kp.", "Kprs.", "kr.", "kst.", "kt.", "ktr.", "kv.", "kvt.", "l.",
        "L.A.", "l.c.", "lab.", "lat.", "lb.m.", "lb.nr.", "lejl.", "lgd.",
        "lic.", "lign.", "lin.", "ling.merc.", "litt.", "Ll.", "loc.cit.",
        "lok.", "lrs.", "ltr.", "m/s", "M/S", "m.a.o.", "m.fl.", "m.m.", "m.v.",
        "m.v.h.", "Mag.", "maks.", "md.", "mdr.", "mdtl.", "mezz.", "mfl.",
        "m.h.p.", "m.h.t", "mht.", "mik.", "min.", "mio.", "modt.", "Mr.",
        "mrk.", "mul.", "mv.", "n.br.", "n.f.", "nat.", "nb.", "Ndr.",
        "nedenst.", "nl.", "nr.", "Nr.", "nto.", "nuv.", "o/m", "o.a.", "o.fl.",
        "o.h.", "o.l.", "o.lign.", "o.m.a.", "o.s.fr.", "obl.", "obs.",
        "odont.", "oecon.", "off.", "ofl.", "omg.", "omkr.", "omr.", "omtr.",
        "opg.", "opl.", "opr.", "org.", "orig.", "osv.", "ovenst.", "overs.",
        "ovf.", "p.", "p.a.", "p.b.a", "p.b.v", "p.c.", "p.m.", "p.m.v.",
        "p.n.", "p.p.", "p.p.s.", "p.s.", "p.t.", "p.v.a.", "p.v.c.", "pag.",
        "par.", "Pas.", "pass.", "pcs.", "pct.", "pd.", "pens.", "pers.",
        "pft.", "pg.", "pga.", "pgl.", "Ph.d.", "pinx.", "pk.", "pkt.",
        "polit.", "polyt.", "pos.", "pp.", "ppm.", "pr.", "prc.", "priv.",
        "prod.", "prof.", "pron.", "Prs.", "præd.", "præf.", "præt.", "psych.",
        "pt.", "pæd.", "q.e.d.", "rad.", "Rcp.", "red.", "ref.", "reg.",
        "regn.", "rel.", "rep.", "repr.", "resp.", "rest.", "rm.", "rtg.",
        "russ.", "s.", "s.br.", "s.d.", "s.f.", "s.m.b.a.", "s.u.", "s.å.",
        "sa.", "sb.", "sc.", "scient.", "scil.", "Sdr.", "sek.", "sekr.",
        "self.", "sem.", "sen.", "shj.", "sign.", "sing.", "sj.", "skr.",
        "Skt.", "slutn.", "sml.", "smp.", "sms.", "snr.", "soc.", "soc.dem.",
        "sort.", "sp.", "spec.", "Spl.", "spm.", "spr.", "spsk.", "statsaut.",
        "st.", "stk.", "str.", "stud.", "subj.", "subst.", "suff.", "sup.",
        "suppl.", "sv.", "såk.", "sædv.", "sø.", "t/r", "t.", "t.h.", "t.o.",
        "t.o.m.", "t.v.", "tab.", "tbl.", "tcp/ip", "td.", "tdl.", "tdr.",
        "techn.", "tekn.", "temp.", "th.", "theol.", "ti.", "tidl.", "tilf.",
        "tilh.", "till.", "tilsv.", "tjg.", "tkr.", "tlf.", "tlgr.", "to.",
        "tr.", "trp.", "tsk.", "tv.", "ty.", "u/b", "udb.", "udbet.", "ugtl.",
        "undt.", "v.", "v.f.", "var.", "vb.", "vedk.", "vedl.", "vedr.",
        "vejl.", "Vg.", "vh.", "vha.", "vs.", "vsa.", "vær.", "zool.", "ø.lgd.",
        "øv.", "øvr.", "årg.", "årh.", ""]:
    _exc[orth] = [{ORTH: orth}]

# Dates
for h in range(1, 31 + 1):
    for period in ["."]:
        _exc["%d%s" % (h, period)] = [
            {ORTH: "%d." % h}]

_custom_base_exc = {
    "i.": [
        {ORTH: "i", LEMMA: "i", NORM: "i"},
        {ORTH: ".", TAG: PUNCT}]
}
_exc.update(_custom_base_exc)


TOKENIZER_EXCEPTIONS = _exc
