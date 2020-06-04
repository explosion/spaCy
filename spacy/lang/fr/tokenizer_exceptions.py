# coding: utf8
from __future__ import unicode_literals

import re

from .punctuation import ELISION, HYPHENS
from ..char_classes import ALPHA_LOWER, ALPHA
from ...symbols import ORTH, LEMMA

# not using the large _tokenizer_exceptions_list by default as it slows down the tokenizer
# from ._tokenizer_exceptions_list import FR_BASE_EXCEPTIONS
FR_BASE_EXCEPTIONS = ["aujourd'hui", "Aujourd'hui"]


def upper_first_letter(text):
    if len(text) == 0:
        return text
    if len(text) == 1:
        return text.upper()
    return text[0].upper() + text[1:]


def lower_first_letter(text):
    if len(text) == 0:
        return text
    if len(text) == 1:
        return text.lower()
    return text[0].lower() + text[1:]


_exc = {"J.-C.": [{LEMMA: "Jésus", ORTH: "J."}, {LEMMA: "Christ", ORTH: "-C."}]}


for exc_data in [
    {LEMMA: "avant", ORTH: "av."},
    {LEMMA: "janvier", ORTH: "janv."},
    {LEMMA: "février", ORTH: "févr."},
    {LEMMA: "avril", ORTH: "avr."},
    {LEMMA: "juillet", ORTH: "juill."},
    {LEMMA: "septembre", ORTH: "sept."},
    {LEMMA: "octobre", ORTH: "oct."},
    {LEMMA: "novembre", ORTH: "nov."},
    {LEMMA: "décembre", ORTH: "déc."},
    {LEMMA: "après", ORTH: "apr."},
    {LEMMA: "docteur", ORTH: "Dr."},
    {LEMMA: "monsieur", ORTH: "M."},
    {LEMMA: "monsieur", ORTH: "Mr."},
    {LEMMA: "madame", ORTH: "Mme."},
    {LEMMA: "mademoiselle", ORTH: "Mlle."},
    {LEMMA: "numéro", ORTH: "n°"},
    {LEMMA: "degrés", ORTH: "d°"},
    {LEMMA: "saint", ORTH: "St."},
    {LEMMA: "sainte", ORTH: "Ste."},
]:
    _exc[exc_data[ORTH]] = [exc_data]


for orth in [
    "après-midi",
    "au-delà",
    "au-dessus",
    "celle-ci",
    "celles-ci",
    "celui-ci",
    "cf.",
    "ci-dessous",
    "elle-même",
    "en-dessous",
    "etc.",
    "jusque-là",
    "lui-même",
    "MM.",
    "No.",
    "peut-être",
    "pp.",
    "quelques-uns",
    "rendez-vous",
    "Vol.",
]:
    _exc[orth] = [{ORTH: orth}]


for verb, verb_lemma in [
    ("a", "avoir"),
    ("est", "être"),
    ("semble", "sembler"),
    ("indique", "indiquer"),
    ("moque", "moquer"),
    ("passe", "passer"),
]:
    for orth in [verb, verb.title()]:
        for pronoun in ["elle", "il", "on"]:
            token = "{}-t-{}".format(orth, pronoun)
            _exc[token] = [
                {LEMMA: verb_lemma, ORTH: orth},  # , TAG: "VERB"},
                {LEMMA: "t", ORTH: "-t"},
                {LEMMA: pronoun, ORTH: "-" + pronoun},
            ]

for verb, verb_lemma in [("est", "être")]:
    for orth in [verb, verb.title()]:
        token = "{}-ce".format(orth)
        _exc[token] = [
            {LEMMA: verb_lemma, ORTH: orth},  # , TAG: "VERB"},
            {LEMMA: "ce", ORTH: "-ce"},
        ]


for pre, pre_lemma in [("qu'", "que"), ("n'", "ne")]:
    for orth in [pre, pre.title()]:
        _exc["%sest-ce" % orth] = [
            {LEMMA: pre_lemma, ORTH: orth},
            {LEMMA: "être", ORTH: "est"},
            {LEMMA: "ce", ORTH: "-ce"},
        ]


for verb, pronoun in [("est", "il"), ("EST", "IL")]:
    token = "{}-{}".format(verb, pronoun)
    _exc[token] = [
        {LEMMA: "être", ORTH: verb},
        {LEMMA: pronoun, ORTH: "-" + pronoun},
    ]


for s, verb, pronoun in [("s", "est", "il"), ("S", "EST", "IL")]:
    token = "{}'{}-{}".format(s, verb, pronoun)
    _exc[token] = [
        {LEMMA: "se", ORTH: s + "'"},
        {LEMMA: "être", ORTH: verb},
        {LEMMA: pronoun, ORTH: "-" + pronoun},
    ]


_infixes_exc = []
orig_elision = "'"
orig_hyphen = "-"

# loop through the elison and hyphen characters, and try to substitute the ones that weren't used in the original list
for infix in FR_BASE_EXCEPTIONS:
    variants_infix = {infix}
    for elision_char in [x for x in ELISION if x != orig_elision]:
        variants_infix.update(
            [word.replace(orig_elision, elision_char) for word in variants_infix]
        )
    for hyphen_char in [x for x in ["-", "‐"] if x != orig_hyphen]:
        variants_infix.update(
            [word.replace(orig_hyphen, hyphen_char) for word in variants_infix]
        )
    variants_infix.update([upper_first_letter(word) for word in variants_infix])
    _infixes_exc.extend(variants_infix)

for orth in _infixes_exc:
    _exc[orth] = [{ORTH: orth}]


_hyphen_prefix = [
    "a[ée]ro",
    "abat",
    "a[fg]ro",
    "after",
    "aigues?",
    "am[ée]ricano",
    "anglo",
    "anti",
    "apr[èe]s",
    "arabo",
    "arcs?",
    "archi",
    "arrières?",
    "audio",
    "avant",
    "avion",
    "auto",
    "banc",
    "bas(?:ses?)?",
    "bateaux?",
    "bec?",
    "belles?",
    "beau",
    "best",
    "bio?",
    "bien",
    "blanc",
    "bo[îi]te",
    "bonn?e?s?",
    "bois",
    "bou(?:c|rg)",
    "b[êe]ta",
    "cache",
    "cap(?:ello)?",
    "casse",
    "castel",
    "champ",
    "chapelle",
    "ch[âa]teau(?:neuf)?",
    "chasse",
    "cha(?:ud|t)e?s?",
    "chauffe",
    "chou",
    "chromo",
    "claire?s?",
    "co(?:de|ca)?",
    "compte",
    "contre",
    "cordon",
    "coupe?",
    "courte?s?",
    "couvre",
    "crash",
    "crise",
    "croche",
    "cross",
    "cyber",
    "côte",
    "demi",
    "di(?:sney)?",
    "dix",
    "d[ée]s?",
    "dys",
    "ex?",
    "émirato",
    "entre",
    "est",
    "ethno",
    "ex",
    "extra",
    "extrême",
    "[ée]co",
    "faux",
    "fil",
    "fort",
    "franco?s?",
    "gallo",
    "gardes?",
    "gastro",
    "grande?",
    "gratte",
    "gr[ée]co",
    "gros",
    "g[ée]o",
    "haute?s?",
    "homm?es?",
    "hors",
    "hyper",
    "indo",
    "infra",
    "inter",
    "intra",
    "islamo",
    "italo",
    "jean",
    "labio",
    "latino",
    "live",
    "lot",
    "louis",
    "m[ai]cro",
    "mal",
    "médio",
    "mesnil",
    "mi(?:ni)?",
    "mono",
    "mont?s?",
    "moyen",
    "multi",
    "m[ée]cano",
    "m[ée]dico",
    "m[ée]do",
    "m[ée]ta",
    "mots?",
    "neuro",
    "noix",
    "non",
    "nord",
    "notre",
    "n[ée]o",
    "ouest",
    "outre",
    "ouvre",
    "passe",
    "perce",
    "pharmaco",
    "ph[oy]to",
    "pieds?",
    "pique",
    "poissons?",
    "ponce",
    "pont",
    "po[rs]t",
    "pousse",
    "primo",
    "pro(?:cès|to)?",
    "pare",
    "petite?s?",
    "plessis",
    "porte",
    "pré",
    "prêchi",
    "protège",
    "pseudo",
    "pêle",
    "péri",
    "puy",
    "quasi",
    "quatre",
    "radio",
    "recourt",
    "rythmo",
    "(?:re)?doubles?",
    "r[ée]",
    "r[ée]tro",
    "requin",
    "sans?",
    "sa?inte?s?",
    "semi",
    "serre",
    "sino",
    "socio",
    "sociale?s?",
    "soixante",
    "sous",
    "su[bdrs]",
    "super",
    "taille",
    "tire",
    "thermo",
    "tiers",
    "tourne",
    "toute?s?",
    "tra[iî]ne?",
    "trans",
    "trente",
    "trois",
    "trousse",
    "tr(?:i|ou)",
    "t[ée]l[ée]",
    "utéro",
    "vaso",
    "vi[cd]e",
    "vid[ée]o",
    "vie(?:ux|i?lles?|i?l)",
    "vill(?:e|eneuve|ers|ette|iers|y)",
    "vingt",
    "voitures?",
    "wagons?",
    "ultra",
    "à",
    "[ée]lectro",
    "[ée]qui",
    "Fontaine",
    "La Chapelle",
    "Marie",
    "Le Mesnil",
    "Neuville",
    "Pierre",
    "Val",
    "Vaux",
]

_regular_exp = [
    "^a[{hyphen}]sexualis[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^arginine[{hyphen}]méthyl[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^binge[{hyphen}]watch[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^black[{hyphen}]out[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^bouche[{hyphen}]por[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^burn[{hyphen}]out[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^by[{hyphen}]pass[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^ch[{elision}]tiis[{al}]+$".format(elision=ELISION, al=ALPHA_LOWER),
    "^chape[{hyphen}]chut[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^down[{hyphen}]load[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^[ée]tats[{hyphen}]uni[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^droits?[{hyphen}]de[{hyphen}]l'homm[{al}]+$".format(
        hyphen=HYPHENS, al=ALPHA_LOWER
    ),
    "^fac[{hyphen}]simil[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^fleur[{hyphen}]bleuis[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^flic[{hyphen}]flaqu[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^fox[{hyphen}]trott[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^google[{hyphen}]is[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^hard[{hyphen}]discount[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^hip[{hyphen}]hop[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^jet[{hyphen}]set[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^knock[{hyphen}]out[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^lèche[{hyphen}]bott[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^litho[{hyphen}]typographi[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^lock[{hyphen}]out[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^lombri[{hyphen}]compost[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^mac[{hyphen}]adamis[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^marque[{hyphen}]pag[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^mouton[{hyphen}]noiris[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^new[{hyphen}]york[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^pair[{hyphen}]programm[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^people[{hyphen}]is[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^plan[{hyphen}]socialis[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^premier[{hyphen}]ministr[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^prud[{elision}]hom[{al}]+$".format(elision=ELISION, al=ALPHA_LOWER),
    "^réarc[{hyphen}]bout[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^refox[{hyphen}]trott[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^remicro[{hyphen}]ond[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^repique[{hyphen}]niqu[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^repetit[{hyphen}]déjeun[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^rick[{hyphen}]roll[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^rond[{hyphen}]ponn[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^shift[{hyphen}]cliqu[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^soudo[{hyphen}]bras[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^stabilo[{hyphen}]boss[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^strip[{hyphen}]teas[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^terra[{hyphen}]form[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^teuf[{hyphen}]teuf[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^yo[{hyphen}]yo[{al}]+$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^zig[{hyphen}]zag[{al}]*$".format(hyphen=HYPHENS, al=ALPHA_LOWER),
    "^z[{elision}]yeut[{al}]+$".format(elision=ELISION, al=ALPHA_LOWER),
]
# catching cases like faux-vampire
_regular_exp += [
    "^{prefix}[{hyphen}][{al}][{hyphen}{al}{elision}]*$".format(
        prefix=p,
        hyphen=HYPHENS,  # putting the - first in the [] range avoids having to use a backslash
        elision=ELISION,
        al=ALPHA_LOWER,
    )
    for p in _hyphen_prefix
]

# catching cases like entr'abat
_elision_prefix = ["r?é?entr", "grande?s?", "r"]
_regular_exp += [
    "^{prefix}[{elision}][{al}][{hyphen}{al}{elision}]*$".format(
        prefix=p, elision=ELISION, hyphen=HYPHENS, al=ALPHA_LOWER
    )
    for p in _elision_prefix
]

# catching cases like saut-de-ski, pet-en-l'air
_hyphen_combination = [
    "l[èe]s?",
    "la",
    "en",
    "des?",
    "d[eu]",
    "sur",
    "sous",
    "aux?",
    "à",
    "et",
    "près",
    "saint",
]
_regular_exp += [
    "^[{a}]+[{hyphen}]{hyphen_combo}[{hyphen}](?:l[{elision}])?[{a}]+$".format(
        hyphen_combo=hc, elision=ELISION, hyphen=HYPHENS, a=ALPHA
    )
    for hc in _hyphen_combination
]


TOKENIZER_EXCEPTIONS = _exc
TOKEN_MATCH = re.compile(
    "(?iu)" + "|".join("(?:{})".format(m) for m in _regular_exp)
).match
