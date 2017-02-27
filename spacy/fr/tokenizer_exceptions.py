# encoding: utf8

from __future__ import unicode_literals

from .. import language_data as base
from ..language_data import strings_to_exc, update_exc
from ..language_data.tokenizer_exceptions import _URL_PATTERN
from ..language_data.punctuation import ALPHA_LOWER

from .punctuation import ELISION, HYPHENS

from ..symbols import *

import os
import io
import re


def get_exceptions():
    from ._tokenizer_exceptions_list import BASE_EXCEPTIONS
    return BASE_EXCEPTIONS


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


def get_tokenizer_exceptions():
    tokenizer_exceptions = strings_to_exc(base.EMOTICONS)
    update_exc(tokenizer_exceptions, strings_to_exc(base.ABBREVIATIONS))

    ABBREVIATIONS_1 = {
        "av.": [
            {LEMMA: "avant", ORTH: "av."}
        ],
        "janv.": [
            {LEMMA: "janvier", ORTH: "janv."}
        ],
        "févr.": [
            {LEMMA: "février", ORTH: "févr."}
        ],
        "avr.": [
            {LEMMA: "avril", ORTH: "avr."}
        ],
        "juill.": [
            {LEMMA: "juillet", ORTH: "juill."}
        ],
        "sept.": [
            {LEMMA: "septembre", ORTH: "sept."}
        ],
        "oct.": [
            {LEMMA: "octobre", ORTH: "oct."}
        ],
        "nov.": [
            {LEMMA: "novembre", ORTH: "nov."}
        ],
        "déc.": [
            {LEMMA: "décembre", ORTH: "déc."}
        ],
        "apr.": [
            {LEMMA: "après", ORTH: "apr."}
        ],
        "J.-C.": [
            {LEMMA: "Jésus", ORTH: "J."},
            {LEMMA: "Christ", ORTH: "-C."}
        ],
        "Dr.": [
            {LEMMA: "docteur", ORTH: "Dr."}
        ],
        "M.": [
            {LEMMA: "monsieur", ORTH: "M."}
        ],
        "Mr.": [
            {LEMMA: "monsieur", ORTH: "Mr."}
        ],
        "Mme.": [
            {LEMMA: "madame", ORTH: "Mme."}
        ],
        "Mlle.": [
            {LEMMA: "mademoiselle", ORTH: "Mlle."}
        ],
        "n°": [
            {LEMMA: "numéro", ORTH: "n°"}
        ],
        "d°": [
            {LEMMA: "degrés", ORTH: "d°"}
        ],
        "St.": [
            {LEMMA: "saint", ORTH: "St."}
        ],
        "Ste.": [
            {LEMMA: "sainte", ORTH: "Ste."}
        ]
    }

    ABBREVIATIONS_2 = [
        "etc.",
    ]

    VERBS = {}
    for verb, verb_lemma in (("a", "avoir"), ("est", "être"),
                             ("semble", "sembler"), ("indique", "indiquer"),
                             ("moque", "moquer"), ("passe", "passer")):
        for pronoun in ("elle", "il", "on"):
            token = "{}-t-{}".format(verb, pronoun)
            VERBS[token] = [
                {LEMMA: verb_lemma, ORTH: verb},
                {LEMMA: "t", ORTH: "-t"},
                {LEMMA: pronoun, ORTH: "-" + pronoun}
            ]

    VERBS['est-ce'] = [
        {LEMMA: 'être', ORTH: "est"},
        {LEMMA: 'ce', ORTH: '-ce'}
    ]

    for pre, pre_lemma in (("qu'", "que"), ("Qu'", "Que"), ("n'", "ne"),
                           ("N'", "Ne")):
        VERBS['{}est-ce'.format(pre)] = [
            {LEMMA: pre_lemma, ORTH: pre},
            {LEMMA: 'être', ORTH: "est"},
            {LEMMA: 'ce', ORTH: '-ce'}
        ]

    HYPHEN = ['-', '‐']

    base_exceptions = get_exceptions()
    infixes_exceptions = []

    for elision_char in ELISION:
        for hyphen_char in HYPHEN:
            infixes_exceptions += [infix.replace("'", elision_char).replace('-', hyphen_char)
                                   for infix in base_exceptions]

    infixes_exceptions += [upper_first_letter(word) for word in infixes_exceptions]

    infixes_exceptions = list(set(infixes_exceptions))

    update_exc(tokenizer_exceptions, strings_to_exc(infixes_exceptions))
    update_exc(tokenizer_exceptions, ABBREVIATIONS_1)
    update_exc(tokenizer_exceptions, strings_to_exc(ABBREVIATIONS_2))
    update_exc(tokenizer_exceptions, VERBS)
    return tokenizer_exceptions


HYPHEN_PREFIX = [
    'a[ée]ro', 'abat', 'a[fg]ro', 'after', 'am[ée]ricano', 'anglo', 'anti', 'apr[èe]s', 'arabo', 'arcs?', 'archi',
    'arrières?', 'avant', 'auto',
    'banc', 'bas(?:ses?)?', 'bec?', 'best', 'bio?', 'bien', 'blanc', 'bo[îi]te', 'bois', 'bou(?:c|rg)', 'b[êe]ta',
    'cache', 'cap(?:ello)?', 'champ', 'chapelle', 'ch[âa]teau', 'cha(?:ud|t)e?s?', 'chou', 'chromo', 'claire?s?',
    'co(?:de|ca)?', 'compte', 'contre', 'cordon', 'coupe?', 'court', 'crash', 'crise', 'croche', 'cross', 'cyber',
    'côte',
    'demi', 'di(?:sney)?', 'd[ée]s?', 'double', 'dys',
    'entre', 'est', 'ethno', 'extra', 'extrême', '[ée]co',
    'fil', 'fort', 'franco?s?',
    'gallo', 'gardes?', 'gastro', 'grande?', 'gratte', 'gr[ée]co', 'gros', 'g[ée]o',
    'haute?s?', 'hyper',
    'indo', 'infra', 'inter', 'intra', 'islamo', 'italo',
    'jean',
    'labio', 'latino', 'live', 'lot', 'louis',
    'm[ai]cro', 'mesnil', 'mi(?:ni)?', 'mono', 'mont?s?', 'moyen', 'multi', 'm[ée]cano', 'm[ée]dico', 'm[ée]do', 'm[ée]ta',
    'mots?',
    'noix', 'non', 'nord', 'notre', 'n[ée]o',
    'ouest', 'outre', 'ouvre',
    'passe', 'perce', 'pharmaco', 'ph[oy]to', 'pique', 'poissons?', 'ponce', 'pont', 'po[rs]t',
    'primo', 'pro(?:cès|to)?', 'pare', 'petite?', 'porte', 'pré', 'prêchi', 'pseudo', 'pêle', 'péri', 'puy',
    'quasi',
    'recourt', 'rythmo', 'r[ée]', 'r[ée]tro',
    'sans', 'sainte?s?', 'semi', 'social', 'sous', 'su[bdr]', 'super',
    'tire', 'thermo', 'tiers', 'trans', 'tr(?:i|ou)', 't[ée]l[ée]',
    'vi[cd]e', 'vid[ée]o', 'vie(?:ux|illes?)', 'vill(?:e|eneuve|ers|ette|iers|y)',
    'ultra',
    'à',
    '[ée]lectro', '[ée]qui'
    ]

ELISION_PREFIX = ['entr', 'grande?s?']

REGULAR_EXP = [
    '^droits?[{hyphen}]de[{hyphen}]l\'homm[{alpha}]+$'.format(hyphen=HYPHENS, alpha=ALPHA_LOWER),
    '^zig[{hyphen}]zag[{alpha}]*$'.format(hyphen=HYPHENS, alpha=ALPHA_LOWER),
    '^prud[{elision}]homm[{alpha}]*$'.format(elision=ELISION, alpha=ALPHA_LOWER),
]

other_hyphens = ''.join([h for h in HYPHENS if h != '-'])

REGULAR_EXP += ["^{prefix}[{hyphen}][{alpha}][{alpha}{elision}{other_hyphen}\-]*$".format(
    prefix=p, hyphen=HYPHENS, other_hyphen=other_hyphens, elision=ELISION, alpha=ALPHA_LOWER)
                for p in HYPHEN_PREFIX]

REGULAR_EXP += ["^{prefix}[{elision}][{alpha}][{alpha}{elision}{hyphen}\-]*$".format(
    prefix=p, elision=HYPHENS, hyphen=other_hyphens, alpha=ALPHA_LOWER)
                for p in ELISION_PREFIX]

REGULAR_EXP.append(_URL_PATTERN)

TOKEN_MATCH = re.compile('|'.join('(?:{})'.format(m) for m in REGULAR_EXP), re.IGNORECASE).match

__all__ = ["get_tokenizer_exceptions", "TOKEN_MATCH"]
