# coding: utf8
from __future__ import unicode_literals

import regex as re

from ._tokenizer_exceptions_list import FR_BASE_EXCEPTIONS
from .punctuation import ELISION, HYPHENS
from ..tokenizer_exceptions import URL_PATTERN
from ..char_classes import ALPHA_LOWER
from ...symbols import ORTH, LEMMA, TAG, NORM, PRON_LEMMA


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


_exc = {
    "J.-C.": [
        {LEMMA: "Jésus", ORTH: "J."},
        {LEMMA: "Christ", ORTH: "-C."}]
}


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
    {LEMMA: "sainte", ORTH: "Ste."}]:
    _exc[exc_data[ORTH]] = [exc_data]


for orth in FR_BASE_EXCEPTIONS + ["etc."]:
    _exc[orth] = [{ORTH: orth}]


for verb, verb_lemma in [
    ("a", "avoir"),
    ("est", "être"),
    ("semble", "sembler"),
    ("indique", "indiquer"),
    ("moque", "moquer"),
    ("passe", "passer")]:
    for orth in [verb, verb.title()]:
        for pronoun in ["elle", "il", "on"]:
            token = "{}-t-{}".format(orth, pronoun)
            _exc[token] = [
                {LEMMA: verb_lemma, ORTH: orth, TAG: "VERB"},
                {LEMMA: "t", ORTH: "-t"},
                {LEMMA: pronoun, ORTH: "-" + pronoun}]

for verb, verb_lemma in [
    ("est","être")]:
    for orth in [verb, verb.title()]:
        token = "{}-ce".format(orth)
        _exc[token] = [
            {LEMMA: verb_lemma, ORTH: orth, TAG: "VERB"},
            {LEMMA: 'ce', ORTH: '-ce'}]


for pre, pre_lemma in [
    ("qu'", "que"),
    ("n'", "ne")]:
    for orth in [pre,pre.title()]:
        _exc['%sest-ce' % orth] = [
            {LEMMA: pre_lemma, ORTH: orth, TAG: "ADV"},
            {LEMMA: 'être', ORTH: "est", TAG: "VERB"},
            {LEMMA: 'ce', ORTH: '-ce'}]


_infixes_exc = []
for elision_char in ELISION:
    for hyphen_char in ['-', '‐']:
        _infixes_exc += [infix.replace("'", elision_char).replace('-', hyphen_char)
                         for infix in FR_BASE_EXCEPTIONS]
_infixes_exc += [upper_first_letter(word) for word in _infixes_exc]
_infixes_exc = list(set(_infixes_exc))

for orth in _infixes_exc:
    _exc[orth] = [{ORTH: orth}]


_hyphen_prefix = [
    'a[ée]ro', 'abat', 'a[fg]ro', 'after', 'am[ée]ricano', 'anglo', 'anti',
    'apr[èe]s', 'arabo', 'arcs?', 'archi', 'arrières?', 'avant', 'auto',
    'banc', 'bas(?:ses?)?', 'bec?', 'best', 'bio?', 'bien', 'blanc', 'bo[îi]te',
    'bois', 'bou(?:c|rg)', 'b[êe]ta', 'cache', 'cap(?:ello)?', 'champ',
    'chapelle', 'ch[âa]teau', 'cha(?:ud|t)e?s?', 'chou', 'chromo', 'claire?s?',
    'co(?:de|ca)?', 'compte', 'contre', 'cordon', 'coupe?', 'court', 'crash',
    'crise', 'croche', 'cross', 'cyber', 'côte', 'demi', 'di(?:sney)?',
    'd[ée]s?', 'double', 'dys', 'entre', 'est', 'ethno', 'extra', 'extrême',
    '[ée]co', 'fil', 'fort', 'franco?s?', 'gallo', 'gardes?', 'gastro',
    'grande?', 'gratte', 'gr[ée]co', 'gros', 'g[ée]o', 'haute?s?', 'hyper',
    'indo', 'infra', 'inter', 'intra', 'islamo', 'italo', 'jean', 'labio',
    'latino', 'live', 'lot', 'louis', 'm[ai]cro', 'mesnil', 'mi(?:ni)?', 'mono',
    'mont?s?', 'moyen', 'multi', 'm[ée]cano', 'm[ée]dico', 'm[ée]do', 'm[ée]ta',
    'mots?', 'noix', 'non', 'nord', 'notre', 'n[ée]o', 'ouest', 'outre', 'ouvre',
    'passe', 'perce', 'pharmaco', 'ph[oy]to', 'pique', 'poissons?', 'ponce',
    'pont', 'po[rs]t', 'primo', 'pro(?:cès|to)?', 'pare', 'petite?', 'porte',
    'pré', 'prêchi', 'pseudo', 'pêle', 'péri', 'puy', 'quasi', 'recourt',
    'rythmo', 'r[ée]', 'r[ée]tro', 'sans', 'sainte?s?', 'semi', 'social',
    'sous', 'su[bdr]', 'super', 'tire', 'thermo', 'tiers', 'trans',
    'tr(?:i|ou)', 't[ée]l[ée]', 'vi[cd]e', 'vid[ée]o', 'vie(?:ux|illes?)',
    'vill(?:e|eneuve|ers|ette|iers|y)', 'ultra', 'à', '[ée]lectro', '[ée]qui']

_elision_prefix = ['entr', 'grande?s?']
_other_hyphens = ''.join([h for h in HYPHENS if h != '-'])

_regular_exp = [
    '^droits?[{hyphen}]de[{hyphen}]l\'homm[{alpha}]+$'.format(hyphen=HYPHENS, alpha=ALPHA_LOWER),
    '^zig[{hyphen}]zag[{alpha}]*$'.format(hyphen=HYPHENS, alpha=ALPHA_LOWER),
    '^prud[{elision}]homm[{alpha}]*$'.format(elision=ELISION, alpha=ALPHA_LOWER)]
_regular_exp += ["^{prefix}[{hyphen}][{alpha}][{alpha}{elision}{other_hyphen}\-]*$".format(
                 prefix=p, hyphen=HYPHENS, other_hyphen=_other_hyphens,
                 elision=ELISION, alpha=ALPHA_LOWER)
                 for p in _hyphen_prefix]
_regular_exp += ["^{prefix}[{elision}][{alpha}][{alpha}{elision}{hyphen}\-]*$".format(
                 prefix=p, elision=HYPHENS, hyphen=_other_hyphens, alpha=ALPHA_LOWER)
                 for p in _elision_prefix]
_regular_exp.append(URL_PATTERN)


TOKENIZER_EXCEPTIONS = _exc
TOKEN_MATCH = re.compile('|'.join('(?:{})'.format(m) for m in _regular_exp), re.IGNORECASE).match
