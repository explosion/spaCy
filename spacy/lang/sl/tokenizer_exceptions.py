from typing import Dict, List
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...symbols import ORTH, NORM
from ...util import update_exc

_exc: Dict[str, List[Dict]] = {}

_other_exc = {
    "t.i.": [{ORTH: "t.", NORM: "tako"}, {ORTH: "i.", NORM: "imenovano"}],
    "t.j.": [{ORTH: "t.", NORM: "to"}, {ORTH: "j.", NORM: "je"}],
    "T.j.": [{ORTH: "T.", NORM: "to"}, {ORTH: "j.", NORM: "je"}],
    "d.o.o.": [
        {ORTH: "d.", NORM: "družba"},
        {ORTH: "o.", NORM: "omejeno"},
        {ORTH: "o.", NORM: "odgovornostjo"},
    ],
    "D.O.O.": [
        {ORTH: "D.", NORM: "družba"},
        {ORTH: "O.", NORM: "omejeno"},
        {ORTH: "O.", NORM: "odgovornostjo"},
    ],
    "d.n.o.": [
        {ORTH: "d.", NORM: "družba"},
        {ORTH: "n.", NORM: "neomejeno"},
        {ORTH: "o.", NORM: "odgovornostjo"},
    ],
    "D.N.O.": [
        {ORTH: "D.", NORM: "družba"},
        {ORTH: "N.", NORM: "neomejeno"},
        {ORTH: "O.", NORM: "odgovornostjo"},
    ],
    "d.d.": [{ORTH: "d.", NORM: "delniška"}, {ORTH: "d.", NORM: "družba"}],
    "D.D.": [{ORTH: "D.", NORM: "delniška"}, {ORTH: "D.", NORM: "družba"}],
    "s.p.": [{ORTH: "s.", NORM: "samostojni"}, {ORTH: "p.", NORM: "podjetnik"}],
    "S.P.": [{ORTH: "S.", NORM: "samostojni"}, {ORTH: "P.", NORM: "podjetnik"}],
    "l.r.": [{ORTH: "l.", NORM: "lastno"}, {ORTH: "r.", NORM: "ročno"}],
    "le-te": [{ORTH: "le"}, {ORTH: "-"}, {ORTH: "te"}],
    "Le-te": [{ORTH: "Le"}, {ORTH: "-"}, {ORTH: "te"}],
    "le-ti": [{ORTH: "le"}, {ORTH: "-"}, {ORTH: "ti"}],
    "Le-ti": [{ORTH: "Le"}, {ORTH: "-"}, {ORTH: "ti"}],
    "le-to": [{ORTH: "le"}, {ORTH: "-"}, {ORTH: "to"}],
    "Le-to": [{ORTH: "Le"}, {ORTH: "-"}, {ORTH: "to"}],
    "le-ta": [{ORTH: "le"}, {ORTH: "-"}, {ORTH: "ta"}],
    "Le-ta": [{ORTH: "Le"}, {ORTH: "-"}, {ORTH: "ta"}],
    "le-tega": [{ORTH: "le"}, {ORTH: "-"}, {ORTH: "tega"}],
    "Le-tega": [{ORTH: "Le"}, {ORTH: "-"}, {ORTH: "tega"}],
}

_exc.update(_other_exc)


for exc_data in [
    {ORTH: "adm.", NORM: "administracija"},
    {ORTH: "aer.", NORM: "aeronavtika"},
    {ORTH: "agr.", NORM: "agronomija"},
    {ORTH: "amer.", NORM: "ameriško"},
    {ORTH: "anat.", NORM: "anatomija"},
    {ORTH: "angl.", NORM: "angleški"},
    {ORTH: "ant.", NORM: "antonim"},
    {ORTH: "antr.", NORM: "antropologija"},
    {ORTH: "apr.", NORM: "april"},
    {ORTH: "arab.", NORM: "arabsko"},
    {ORTH: "arheol.", NORM: "arheologija"},
    {ORTH: "arhit.", NORM: "arhitektura"},
    {ORTH: "avg.", NORM: "avgust"},
    {ORTH: "avstr.", NORM: "avstrijsko"},
    {ORTH: "avt.", NORM: "avtomobilizem"},
    {ORTH: "bibl.", NORM: "biblijsko"},
    {ORTH: "biokem.", NORM: "biokemija"},
    {ORTH: "biol.", NORM: "biologija"},
    {ORTH: "bolg.", NORM: "bolgarski"},
    {ORTH: "bot.", NORM: "botanika"},
    {ORTH: "cit.", NORM: "citat"},
    {ORTH: "daj.", NORM: "dajalnik"},
    {ORTH: "del.", NORM: "deležnik"},
    {ORTH: "ed.", NORM: "ednina"},
    {ORTH: "etn.", NORM: "etnografija"},
    {ORTH: "farm.", NORM: "farmacija"},
    {ORTH: "filat.", NORM: "filatelija"},
    {ORTH: "filoz.", NORM: "filozofija"},
    {ORTH: "fin.", NORM: "finančništvo"},
    {ORTH: "fiz.", NORM: "fizika"},
    {ORTH: "fot.", NORM: "fotografija"},
    {ORTH: "fr.", NORM: "francoski"},
    {ORTH: "friz.", NORM: "frizerstvo"},
    {ORTH: "gastr.", NORM: "gastronomija"},
    {ORTH: "geogr.", NORM: "geografija"},
    {ORTH: "geol.", NORM: "geologija"},
    {ORTH: "geom.", NORM: "geometrija"},
    {ORTH: "germ.", NORM: "germanski"},
    {ORTH: "gl.", NORM: "glej"},
    {ORTH: "glag.", NORM: "glagolski"},
    {ORTH: "glasb.", NORM: "glasba"},
    {ORTH: "gled.", NORM: "gledališče"},
    {ORTH: "gost.", NORM: "gostinstvo"},
    {ORTH: "gozd.", NORM: "gozdarstvo"},
    {ORTH: "gr.", NORM: "grški"},
    {ORTH: "grad.", NORM: "gradbeništvo"},
    {ORTH: "hebr.", NORM: "hebrejsko"},
    {ORTH: "hrv.", NORM: "hrvaško"},
    {ORTH: "ide.", NORM: "indoevropsko"},
    {ORTH: "igr.", NORM: "igre"},
    {ORTH: "im.", NORM: "imenovalnik"},
    {ORTH: "iron.", NORM: "ironično"},
    {ORTH: "it.", NORM: "italijanski"},
    {ORTH: "itd.", NORM: "in tako dalje"},
    {ORTH: "itn.", NORM: "in tako naprej"},
    {ORTH: "ipd.", NORM: "in podobno"},
    {ORTH: "jap.", NORM: "japonsko"},
    {ORTH: "jul.", NORM: "julij"},
    {ORTH: "jun.", NORM: "junij"},
    {ORTH: "kit.", NORM: "kitajsko"},
    {ORTH: "knj.", NORM: "knjižno"},
    {ORTH: "knjiž.", NORM: "knjižno"},
    {ORTH: "kor.", NORM: "koreografija"},
    {ORTH: "lat.", NORM: "latinski"},
    {ORTH: "les.", NORM: "lesna stroka"},
    {ORTH: "lingv.", NORM: "lingvistika"},
    {ORTH: "lit.", NORM: "literarni"},
    {ORTH: "ljubk.", NORM: "ljubkovalno"},
    {ORTH: "lov.", NORM: "lovstvo"},
    {ORTH: "m.", NORM: "moški"},
    {ORTH: "mak.", NORM: "makedonski"},
    {ORTH: "mar.", NORM: "marec"},
    {ORTH: "mat.", NORM: "matematika"},
    {ORTH: "med.", NORM: "medicina"},
    {ORTH: "meh.", NORM: "mehiško"},
    {ORTH: "mest.", NORM: "mestnik"},
    {ORTH: "mdr.", NORM: "med drugim"},
    {ORTH: "min.", NORM: "mineralogija"},
    {ORTH: "mitol.", NORM: "mitologija"},
    {ORTH: "mn.", NORM: "množina"},
    {ORTH: "mont.", NORM: "montanistika"},
    {ORTH: "muz.", NORM: "muzikologija"},
    {ORTH: "nam.", NORM: "namenilnik"},
    {ORTH: "nar.", NORM: "narečno"},
    {ORTH: "nav.", NORM: "navadno"},
    {ORTH: "nedol.", NORM: "nedoločnik"},
    {ORTH: "nedov.", NORM: "nedovršni"},
    {ORTH: "neprav.", NORM: "nepravilno"},
    {ORTH: "nepreh.", NORM: "neprehodno"},
    {ORTH: "neskl.", NORM: "nesklonljiv(o)"},
    {ORTH: "nestrok.", NORM: "nestrokovno"},
    {ORTH: "num.", NORM: "numizmatika"},
    {ORTH: "npr.", NORM: "na primer"},
    {ORTH: "obrt.", NORM: "obrtništvo"},
    {ORTH: "okt.", NORM: "oktober"},
    {ORTH: "or.", NORM: "orodnik"},
    {ORTH: "os.", NORM: "oseba"},
    {ORTH: "otr.", NORM: "otroško"},
    {ORTH: "oz.", NORM: "oziroma"},
    {ORTH: "pal.", NORM: "paleontologija"},
    {ORTH: "papir.", NORM: "papirništvo"},
    {ORTH: "ped.", NORM: "pedagogika"},
    {ORTH: "pisar.", NORM: "pisarniško"},
    {ORTH: "pog.", NORM: "pogovorno"},
    {ORTH: "polit.", NORM: "politika"},
    {ORTH: "polj.", NORM: "poljsko"},
    {ORTH: "poljud.", NORM: "poljudno"},
    {ORTH: "preg.", NORM: "pregovor"},
    {ORTH: "preh.", NORM: "prehodno"},
    {ORTH: "pren.", NORM: "preneseno"},
    {ORTH: "prid.", NORM: "pridevnik"},
    {ORTH: "prim.", NORM: "primerjaj"},
    {ORTH: "prisl.", NORM: "prislov"},
    {ORTH: "psih.", NORM: "psihologija"},
    {ORTH: "psiht.", NORM: "psihiatrija"},
    {ORTH: "rad.", NORM: "radiotehnika"},
    {ORTH: "rač.", NORM: "računalništvo"},
    {ORTH: "rib.", NORM: "ribištvo"},
    {ORTH: "rod.", NORM: "rodilnik"},
    {ORTH: "rus.", NORM: "rusko"},
    {ORTH: "s.", NORM: "srednji"},
    {ORTH: "sam.", NORM: "samostalniški"},
    {ORTH: "sed.", NORM: "sedanjik"},
    {ORTH: "sep.", NORM: "september"},
    {ORTH: "slabš.", NORM: "slabšalno"},
    {ORTH: "slovan.", NORM: "slovansko"},
    {ORTH: "slovaš.", NORM: "slovaško"},
    {ORTH: "srb.", NORM: "srbsko"},
    {ORTH: "star.", NORM: "starinsko"},
    {ORTH: "stil.", NORM: "stilno"},
    {ORTH: "sv.", NORM: "svet(i)"},
    {ORTH: "teh.", NORM: "tehnika"},
    {ORTH: "tisk.", NORM: "tiskarstvo"},
    {ORTH: "tj.", NORM: "to je"},
    {ORTH: "tož.", NORM: "tožilnik"},
    {ORTH: "trg.", NORM: "trgovina"},
    {ORTH: "ukr.", NORM: "ukrajinski"},
    {ORTH: "um.", NORM: "umetnost"},
    {ORTH: "vel.", NORM: "velelnik"},
    {ORTH: "vet.", NORM: "veterina"},
    {ORTH: "vez.", NORM: "veznik"},
    {ORTH: "vn.", NORM: "visokonemško"},
    {ORTH: "voj.", NORM: "vojska"},
    {ORTH: "vrtn.", NORM: "vrtnarstvo"},
    {ORTH: "vulg.", NORM: "vulgarno"},
    {ORTH: "vznes.", NORM: "vzneseno"},
    {ORTH: "zal.", NORM: "založništvo"},
    {ORTH: "zastar.", NORM: "zastarelo"},
    {ORTH: "zgod.", NORM: "zgodovina"},
    {ORTH: "zool.", NORM: "zoologija"},
    {ORTH: "čeb.", NORM: "čebelarstvo"},
    {ORTH: "češ.", NORM: "češki"},
    {ORTH: "člov.", NORM: "človeškost"},
    {ORTH: "šah.", NORM: "šahovski"},
    {ORTH: "šalj.", NORM: "šaljivo"},
    {ORTH: "šp.", NORM: "španski"},
    {ORTH: "špan.", NORM: "špansko"},
    {ORTH: "šport.", NORM: "športni"},
    {ORTH: "štev.", NORM: "števnik"},
    {ORTH: "šved.", NORM: "švedsko"},
    {ORTH: "švic.", NORM: "švicarsko"},
    {ORTH: "ž.", NORM: "ženski"},
    {ORTH: "žarg.", NORM: "žargonsko"},
    {ORTH: "žel.", NORM: "železnica"},
    {ORTH: "živ.", NORM: "živost"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


abbrv = """
Co. Ch. DIPL. DR. Dr. Ev. Inc. Jr. Kr. Mag. M. MR. Mr. Mt. Murr. Npr. OZ. 
Opr. Osn. Prim. Roj. ST. Sim. Sp. Sred. St. Sv. Škofl. Tel. UR. Zb. 
a. aa. ab. abc. abit. abl. abs. abt. acc. accel. add. adj. adv. aet. afr. akad. al. alban. all. alleg. 
alp. alt. alter. alžir. am. an. andr. ang. anh. anon. ans. antrop. apoc. app. approx. apt. ar. arc. arch. 
arh. arr. as. asist. assist. assoc. asst. astr. attn. aug. avstral. az. b. bab. bal. bbl. bd. belg. bioinf. 
biomed. bk. bl. bn. borg. bp. br. braz. brit. bros. broš. bt. bu. c. ca. cal. can. cand. cantab. cap. capt.
cat. cath. cc. cca. cd. cdr. cdre. cent. cerkv. cert. cf. cfr. ch. chap. chem. chr. chs. cic. circ. civ. cl.
cm. cmd. cnr. co. cod. col. coll. colo. com. comp. con. conc. cond. conn. cons. cont. coop. corr. cost. cp.
cpl. cr. crd. cres. cresc. ct. cu. d. dan. dat. davč. ddr. dec. ded. def. dem. dent. dept. dia. dip. dipl. 
dir. disp. diss. div. do. doc. dok. dol. doo. dop. dott. dr. dram. druž. družb. drž. dt. duh. dur. dvr. dwt. e.
ea. ecc. eccl. eccles. econ. edn. egipt. egr. ekon. eksp. el. em. enc. eng. eo. ep. err. esp. esq. est.
et. etc. etnogr. etnol. ev. evfem. evr. ex. exc. excl. exp. expl. ext. exx. f. fa. facs. fak. faks. fas.
fasc. fco. fcp. feb. febr. fec. fed. fem. ff. fff. fid. fig. fil. film. fiziol. fiziot. flam. fm. fo. fol. folk.
frag. fran. franc. fsc. g. ga. gal. gdč. ge. gen. geod. geog. geotehnol. gg. gimn. glas. glav. gnr. go. gor.
gosp. gp. graf. gram. gren. grš. gs. h. hab. hf. hist. ho. hort. i. ia. ib. ibid. id. idr. idridr. ill. imen.
imp. impf. impr. in. inc. incl. ind. indus. inf. inform. ing. init. ins. int. inv. inšp. inštr. inž. is. islam.
ist. ital. iur. iz. izbr. izd. izg. izgr. izr. izv. j. jak. jam. jan. jav. je. jez. jr. jsl. jud. jug.
jugoslovan. jur. juž. jv. jz. k. kal. kan. kand. kat. kdo. kem. kip. kmet. kol. kom. komp. konf. kont. kost. kov. 
kp. kpfw. kr. kraj. krat. kub. kult. kv. kval. l. la. lab. lb. ld. let. lib. lik. litt. lj. ljud. ll. loc. log. 
loč. lt. ma. madž. mag. manag. manjš. masc. mass. mater. max. maxmax. mb. md. mech. medic. medij. medn. 
mehč. mem. menedž. mes. mess. metal. meteor. meteorol. mex. mi. mikr. mil. minn. mio. misc. miss. mit. mk. 
mkt. ml. mlad. mlle. mlr. mm. mme. množ. mo. moj. moš. možn. mr. mrd. mrs. ms. msc. msgr. mt. murr. mus. mut. 
n. na. nad. nadalj. nadom. nagl. nakl. namer. nan. naniz. nasl. nat. navt. nač. ned. nem. nik. nizoz. nm. nn. 
no. nom. norv. notr. nov. novogr. ns. o. ob. obd. obj. oblač. obl. oblik. obr. obraz. obs. obst. obt. obč. oc. 
oct. od. odd. odg. odn. odst. odv. oec. off. ok. okla. okr. ont. oo. op. opis. opp. opr. orch. ord. ore. oreg. 
org. orient. orig. ork. ort. oseb. osn. ot. ozir. ošk. p. pag. par. para. parc. parl. part. past. pat. pdk. 
pen. perf. pert. perz. pesn. pet. pev. pf. pfc. ph. pharm. phil. pis. pl. po. pod. podr. podaljš. pogl. pogoj. pojm. 
pok. pokr. pol. poljed. poljub. polu. pom. pomen. pon. ponov. pop. por. port. pos. posl. posn. pov. pp. ppl. pr. 
praet. prav. pravopis. pravosl. preb. pred. predl. predm. predp. preds. pref. pregib. prel. prem. premen. prep. 
pres. pret. prev. pribl. prih. pril. primerj. primor. prip. pripor. prir. prist. priv. proc. prof. prog. proiz. 
prom. pron. prop. prot. protest. prov. ps. pss. pt. publ. pz. q. qld. qu. quad. que. r. racc. rastl. razgl. 
razl. razv. rd. red. ref. reg. rel. relig. rep. repr. rer. resp. rest. ret. rev. revol. rež. rim. rist. rkp. rm. 
roj. rom. romun. rp. rr. rt. rud. ruš. ry. sal. samogl. san. sc. scen. sci. scr. sdv. seg. sek. sen. sept. ser. 
sev. sg. sgt. sh. sig. sigg. sign. sim. sin. sing. sinh. skand. skl. sklad. sklanj. sklep. skr. sl. slik. slov. 
slovak. slovn. sn. so. sob. soc. sociol. sod. sopomen. sopr. sor. sov. sovj. sp. spec. spl. spr. spreg. sq. sr. 
sre. sred. sredoz. srh. ss. ssp. st. sta. stan. stanstar. stcsl. ste. stim. stol. stom. str. stroj. strok. stsl. 
stud. sup. supl. suppl. svet. sz. t. tab. tech. ted. tehn. tehnol. tek. teks. tekst. tel. temp. ten. teol. ter. 
term. test. th. theol. tim. tip. tisočl. tit. tl. tol. tolmač. tom. tor. tov. tr. trad. traj. trans. tren. 
trib. tril. trop. trp. trž. ts. tt. tu. tur. turiz. tvor. tvorb. tč. u. ul. umet. un. univ. up. upr. ur. urad. 
us. ust. utr. v. va. val. var. varn. ven. ver. verb. vest. vezal. vic. vis. viv. viz. viš. vod. vok. vol. vpr. 
vrst. vrstil. vs. vv. vzd. vzg. vzh. vzor. w. wed. wg. wk. x. y. z. zah. zaim. zak. zap. zasl. zavar. zač. zb. 
združ. zg. zn. znan. znanstv. zoot. zun. zv. zvd. á. é. ć. č. čas. čet. čl. člen. čustv. đ. ľ. ł. ş. ŠT. š. šir. 
škofl. škot. šol. št. števil. štud. ů. ű. žen. žival. 
""".split()

for orth in abbrv:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)
