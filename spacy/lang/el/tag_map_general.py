# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from ...symbols import POS, PUNCT, SYM, ADJ, CCONJ, SCONJ, NUM, DET, ADV, ADP, X, VERB
from ...symbols import NOUN, PROPN, PART, INTJ,SPACE,PRON

TAG_MAP = {
    "Adjective":    {POS:ADJ},
    "Adposition":    {POS:ADP},
    "Adverb":    {POS:ADV},
    "Conjuction_Coordinating":    {POS:CCONJ},
    "Conjuction_Subordinating":    {POS:SCONJ},
    "Determiner":    {POS:DET},
    "Interjection":    {POS:INTJ},
    "Noun_Common":    {POS:NOUN},
    "Noun_Proper":    {POS:PROPN},
    "Numeral":    {POS:NUM},
    "Other":    {POS:X},
    "Particle":    {POS:PART},
    "Pronoun":    {POS:PRON},
    "Punctuation":    {POS:PUNCT},
    "Symbol":    {POS:SYM},
    "Verb":    {POS:VERB}
}
