# coding: utf8
from __future__ import unicode_literals

from ...symbols import POS, PUNCT, ADJ, CCONJ, SCONJ, NUM, DET, ADV
from ...symbols import ADP, X, VERB, NOUN, PROPN, PART, INTJ, PRON


# Tag mappings according to https://universaldependencies.org/tagset-conversion/sv-suc-uposf.html
# for https://github.com/UniversalDependencies/UD_Swedish-Talbanken

TAG_MAP = {
    "AB": {POS: ADV},  # inte, också, så, bara, nu
    "AB|AN": {POS: ADV},  # t.ex., ca, t_ex, bl.a., s_k
    "AB|KOM": {POS: ADV},  # mer, tidigare, mindre, vidare, mera
    "AB|POS": {POS: ADV},  # mycket, helt, ofta, länge, långt
    "AB|SMS": {POS: ADV},  # över-, in-
    "AB|SUV": {POS: ADV},  # minst, mest, högst, främst, helst
    "DT|MAS|SIN|DEF": {POS: DET},
    "DT|MAS|SIN|IND": {POS: DET},
    "DT|NEU|SIN|DEF": {POS: DET},  # det, detta
    "DT|NEU|SIN|IND": {POS: DET},  # ett, något, inget, vart, vartannat
    "DT|NEU|SIN|IND/DEF": {POS: DET},  # allt
    "DT|UTR/NEU|PLU|DEF": {POS: DET},  # de, dessa, bägge, dom
    "DT|UTR/NEU|PLU|IND": {POS: DET},  # några, inga
    "DT|UTR/NEU|PLU|IND/DEF": {POS: DET},  # alla
    "DT|UTR/NEU|SIN/PLU|IND": {POS: DET},  # samma
    "DT|UTR/NEU|SIN|DEF": {POS: DET},  # vardera
    "DT|UTR/NEU|SIN|IND": {POS: DET},  # varje, varenda
    "DT|UTR|SIN|DEF": {POS: DET},  # den, denna
    "DT|UTR|SIN|IND": {POS: DET},  # en, någon, ingen, var, varannan
    "DT|UTR|SIN|IND/DEF": {POS: DET},  # all
    "HA": {POS: ADV},  # när, där, hur, som, då
    "HD|NEU|SIN|IND": {POS: DET},  # vilket
    "HD|UTR/NEU|PLU|IND": {POS: DET},  # vilka
    "HD|UTR|SIN|IND": {POS: DET},  # vilken
    "HP|-|-|-": {POS: PRON},  # som
    "HP|NEU|SIN|IND": {POS: PRON},  # vad, vilket
    "HP|NEU|SIN|IND|SMS": {POS: PRON},
    "HP|UTR/NEU|PLU|IND": {POS: PRON},  # vilka
    "HP|UTR|SIN|IND": {POS: PRON},  # vilken, vem
    "HS|DEF": {POS: DET},  # vars, vilkas, Vems
    "IE": {POS: PART},  # att
    "IN": {POS: INTJ},  # Jo, ja, nej, fan, visst
    "JJ|AN": {POS: ADJ},  # ev, S:t, Kungl, Kungl., Teol
    "JJ|KOM|UTR/NEU|SIN/PLU|IND/DEF|GEN": {POS: ADJ},  # äldres
    "JJ|KOM|UTR/NEU|SIN/PLU|IND/DEF|NOM": {
        POS: ADJ
    },  # större, högre, mindre, bättre, äldre
    "JJ|KOM|UTR/NEU|SIN/PLU|IND/DEF|SMS": {POS: ADJ},
    "JJ|POS|MAS|SIN|DEF|GEN": {POS: ADJ},  # enskildes, sjukes, andres
    "JJ|POS|MAS|SIN|DEF|NOM": {POS: ADJ},  # enskilde, sjuke, andre, unge, ene
    "JJ|POS|NEU|SIN|IND/DEF|NOM": {POS: ADJ},  # eget
    "JJ|POS|NEU|SIN|IND|GEN": {POS: ADJ},
    "JJ|POS|NEU|SIN|IND|NOM": {POS: ADJ},  # annat, svårt, möjligt, nytt, sådant
    "JJ|POS|UTR/NEU|PLU|IND/DEF|GEN": {
        POS: ADJ
    },  # ogiftas, ungas, frånskildas, efterkommandes, färgblindas
    "JJ|POS|UTR/NEU|PLU|IND/DEF|NOM": {POS: ADJ},  # olika, andra, många, stora, vissa
    "JJ|POS|UTR/NEU|PLU|IND|NOM": {POS: ADJ},  # flera, sådana, fler, få, samtliga
    "JJ|POS|UTR/NEU|SIN/PLU|IND|NOM": {POS: ADJ},
    "JJ|POS|UTR/NEU|SIN/PLU|IND/DEF|NOM": {POS: ADJ},  # bra, ena, enda, nästa, ringa
    "JJ|POS|UTR/NEU|SIN|DEF|GEN": {POS: ADJ},
    "JJ|POS|UTR/NEU|SIN|DEF|NOM": {POS: ADJ},  # hela, nya, andra, svenska, ekonomiska
    "JJ|POS|UTR|-|-|SMS": {POS: ADJ},  # fri-, låg-, sexual-
    "JJ|POS|UTR|SIN|IND/DEF|NOM": {POS: ADJ},  # egen
    "JJ|POS|UTR|SIN|IND|GEN": {POS: ADJ},  # enskilds
    "JJ|POS|UTR|SIN|IND|NOM": {POS: ADJ},  # stor, annan, själv, sådan, viss
    "JJ|SUV|MAS|SIN|DEF|GEN": {POS: ADJ},
    "JJ|SUV|MAS|SIN|DEF|NOM": {POS: ADJ},  # störste, främste, äldste, minste
    "JJ|SUV|UTR/NEU|PLU|DEF|NOM": {POS: ADJ},  # flesta
    "JJ|SUV|UTR/NEU|PLU|IND|NOM": {POS: ADJ},
    "JJ|SUV|UTR/NEU|SIN/PLU|DEF|NOM": {
        POS: ADJ
    },  # bästa, största, närmaste, viktigaste, högsta
    "JJ|SUV|UTR/NEU|SIN/PLU|IND|NOM": {
        POS: ADJ
    },  # störst, bäst, tidigast, högst, fattigast
    "KN": {POS: CCONJ},  # och, eller, som, än, men
    "KN|AN": {POS: CCONJ},
    "MAD": {POS: PUNCT},  # ., ?, :, !, ...
    "MID": {POS: PUNCT},  # ,, -, :, *, ;
    "NN|-|-|-|-": {POS: NOUN},  # godo, fjol, fullo, somras, måtto
    "NN|AN": {POS: NOUN},  # kr, %, s., dr, kap.
    "NN|NEU|-|-|-": {POS: NOUN},
    "NN|NEU|-|-|SMS": {POS: NOUN},  # yrkes-, barn-, hem-, fack-, vatten-
    "NN|NEU|PLU|DEF|GEN": {
        POS: NOUN
    },  # barnens, årens, u-ländernas, företagens, århundradenas
    "NN|NEU|PLU|DEF|NOM": {POS: NOUN},  # barnen, u-länderna, åren, länderna, könen
    "NN|NEU|PLU|IND|GEN": {POS: NOUN},  # slags, års, barns, länders, tusentals
    "NN|NEU|PLU|IND|NOM": {POS: NOUN},  # barn, år, fall, länder, problem
    "NN|NEU|SIN|DEF|GEN": {
        POS: NOUN
    },  # äktenskapets, samhällets, barnets, 1800-talets, 1960-talets
    "NN|NEU|SIN|DEF|NOM": {
        POS: NOUN
    },  # äktenskapet, samhället, barnet, stället, hemmet
    "NN|NEU|SIN|IND|GEN": {POS: NOUN},  # års, slags, lands, havs, företags
    "NN|NEU|SIN|IND|NOM": {POS: NOUN},  # år, arbete, barn, sätt, äktenskap
    "NN|SMS": {POS: NOUN},  # PCB-, Syd-
    "NN|UTR|-|-|-": {POS: NOUN},  # dags, rätta
    "NN|UTR|-|-|SMS": {POS: NOUN},  # far-, kibbutz-, röntgen-, barna-, hälso-
    "NN|UTR|PLU|DEF|GEN": {
        POS: NOUN
    },  # föräldrarnas, kvinnornas, elevernas, kibbutzernas, makarnas
    "NN|UTR|PLU|DEF|NOM": {
        POS: NOUN
    },  # kvinnorna, föräldrarna, makarna, männen, hyrorna
    "NN|UTR|PLU|IND|GEN": {POS: NOUN},  # människors, kvinnors, dagars, tiders, månaders
    "NN|UTR|PLU|IND|NOM": {POS: NOUN},  # procent, människor, kvinnor, miljoner, kronor
    "NN|UTR|SIN|DEF|GEN": {POS: NOUN},  # kvinnans, världens, familjens, dagens, jordens
    "NN|UTR|SIN|DEF|NOM": {POS: NOUN},  # familjen, kvinnan, mannen, världen, skolan
    "NN|UTR|SIN|IND|GEN": {POS: NOUN},  # sorts, medelålders, makes, kvinnas, veckas
    "NN|UTR|SIN|IND|NOM": {POS: NOUN},  # del, tid, dag, fråga, man
    "PAD": {POS: PUNCT},  # , ), (
    "PC|AN": {POS: VERB},
    "PC|PRF|MAS|SIN|DEF|GEN": {POS: VERB},  # avlidnes
    "PC|PRF|MAS|SIN|DEF|NOM": {POS: VERB},
    "PC|PRF|NEU|SIN|IND|NOM": {POS: VERB},  # taget, sett, särskilt, förbjudet, ökat
    "PC|PRF|UTR/NEU|PLU|IND/DEF|GEN": {POS: VERB},  # försäkrades, anställdas
    "PC|PRF|UTR/NEU|PLU|IND/DEF|NOM": {
        POS: VERB
    },  # särskilda, gifta, ökade, handikappade, skilda
    "PC|PRF|UTR/NEU|SIN|DEF|GEN": {POS: VERB},
    "PC|PRF|UTR/NEU|SIN|DEF|NOM": {POS: VERB},  # ökade, gifta, nämnda, nedärvda, dolda
    "PC|PRF|UTR|SIN|IND|GEN": {POS: VERB},
    "PC|PRF|UTR|SIN|IND|NOM": {POS: VERB},  # särskild, ökad, beredd, gift, oförändrad
    "PC|PRS|UTR/NEU|SIN/PLU|IND/DEF|GEN": {
        POS: VERB
    },  # studerandes, sammanboendes, dubbelarbetandes
    "PC|PRS|UTR/NEU|SIN/PLU|IND/DEF|NOM": {
        POS: VERB
    },  # följande, beroende, nuvarande, motsvarande, liknande
    "PL": {POS: PART},  # ut, upp, in, till, med
    "PL|SMS": {POS: PART},
    "PM": {POS: PROPN},  # F, N, Liechtenstein, Danmark, DK
    "PM|GEN": {POS: PROPN},  # Sveriges, EEC:s, Guds, Stockholms, Kristi
    "PM|NOM": {POS: PROPN},  # Sverige, EEC, Stockholm, USA, ATP
    "PM|SMS": {POS: PROPN},  # Göteborgs-, Nord-, Väst-
    "PN|MAS|SIN|DEF|SUB/OBJ": {POS: PRON},  # denne
    "PN|NEU|SIN|DEF|SUB/OBJ": {POS: PRON},  # det, detta, detsamma
    "PN|NEU|SIN|IND|SUB/OBJ": {POS: PRON},  # något, allt, mycket, annat, ingenting
    "PN|UTR/NEU|PLU|DEF|OBJ": {POS: PRON},  # dem, varandra, varann
    "PN|UTR/NEU|PLU|DEF|SUB": {POS: PRON},  # de, bägge
    "PN|UTR/NEU|PLU|DEF|SUB/OBJ": {POS: PRON},  # dessa, dom, båda, den, bådadera
    "PN|UTR/NEU|PLU|IND|SUB/OBJ": {POS: PRON},  # andra, alla, många, sådana, några
    "PN|UTR/NEU|SIN/PLU|DEF|OBJ": {POS: PRON},  # sig, sej
    "PN|UTR|PLU|DEF|OBJ": {POS: PRON},  # oss, er, eder
    "PN|UTR|PLU|DEF|SUB": {POS: PRON},  # vi
    "PN|UTR|SIN|DEF|OBJ": {POS: PRON},  # dig, mig, henne, honom, Er
    "PN|UTR|SIN|DEF|SUB": {POS: PRON},  # du, han, hon, jag, ni
    "PN|UTR|SIN|DEF|SUB/OBJ": {POS: PRON},  # den, denna, densamma
    "PN|UTR|SIN|IND|SUB": {POS: PRON},  # man
    "PN|UTR|SIN|IND|SUB/OBJ": {POS: PRON},  # en, var, någon, ingen, Varannan
    "PP": {POS: ADP},  # i, av, på, för, till
    "PP|AN": {POS: ADP},  # f
    "PS|AN": {POS: DET},
    "PS|NEU|SIN|DEF": {POS: DET},  # sitt, vårt, ditt, mitt, ert
    "PS|UTR/NEU|PLU|DEF": {POS: DET},  # sina, våra, dina, mina
    "PS|UTR/NEU|SIN/PLU|DEF": {POS: DET},  # deras, dess, hans, hennes, varandras
    "PS|UTR|SIN|DEF": {POS: DET},  # sin, vår, din, min, er
    "RG": {POS: NUM},  # 2, 17, 20, 1, 18
    "RG|GEN": {POS: NUM},
    "RG|MAS|SIN|DEF|NOM": {POS: NUM},
    "RG|NEU|SIN|IND|NOM": {POS: NUM},  # ett
    "RG|NOM": {POS: NUM},  # två, tre, 1, 20, 2
    "RG|SMS": {POS: NUM},  # ett-, 1950-, två-, tre-, 1700-
    "RG|UTR/NEU|SIN|DEF|NOM": {POS: NUM},
    "RG|UTR|SIN|IND|NOM": {POS: NUM},  # en
    "RO|MAS|SIN|IND/DEF|GEN": {POS: ADJ},
    "RO|MAS|SIN|IND/DEF|NOM": {POS: ADJ},  # förste
    "RO|GEN": {POS: ADJ},
    "RO|NOM": {POS: ADJ},  # första, andra, tredje, fjärde, femte
    "SN": {POS: SCONJ},  # att, om, innan, eftersom, medan
    "UO": {POS: X},  # companionship, vice, versa, family, capita
    "VB|AN": {POS: VERB},  # jfr
    "VB|IMP|AKT": {POS: VERB},  # se, Diskutera, låt, Läs, Gå
    "VB|IMP|SFO": {POS: VERB},  # tas
    "VB|INF|AKT": {POS: VERB},  # vara, få, ha, bli, kunna
    "VB|INF|SFO": {POS: VERB},  # användas, finnas, göras, tas, ses
    "VB|KON|PRS|AKT": {POS: VERB},  # vare, Gånge
    "VB|KON|PRT|AKT": {POS: VERB},  # vore, finge
    "VB|KON|PRT|SFO": {POS: VERB},
    "VB|PRS|AKT": {POS: VERB},  # är, har, kan, får, måste
    "VB|PRS|SFO": {POS: VERB},  # finns, kallas, behövs, beräknas, används
    "VB|PRT|AKT": {POS: VERB},  # skulle, var, hade, kunde, fick
    "VB|PRT|SFO": {POS: VERB},  # fanns, gjordes, höjdes, användes, infördes
    "VB|SMS": {POS: VERB},  # läs-
    "VB|SUP|AKT": {POS: VERB},  # varit, fått, blivit, haft, kommit
    "VB|SUP|SFO": {POS: VERB},  # nämnts, gjorts, förändrats, sagts, framhållits
}
