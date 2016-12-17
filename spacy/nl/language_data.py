# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA
from ..language_data import TOKENIZER_PREFIXES
from ..language_data import TOKENIZER_SUFFIXES
from ..language_data import TOKENIZER_INFIXES


# TODO insert TAG_MAP for Dutch

TAG_MAP = {
    "ADV":      {POS: "ADV"},
    "NOUN":     {POS: "NOUN"},
    "ADP":      {POS: "ADP"},
    "PRON":     {POS: "PRON"},
    "SCONJ":    {POS: "SCONJ"},
    "PROPN":    {POS: "PROPN"},
    "DET":      {POS: "DET"},
    "SYM":      {POS: "SYM"},
    "INTJ":     {POS: "INTJ"},
    "PUNCT":    {POS: "PUNCT"},
    "NUM":      {POS: "NUM"},
    "AUX":      {POS: "AUX"},
    "X":        {POS: "X"},
    "CONJ":     {POS: "CONJ"},
    "ADJ":      {POS: "ADJ"},
    "VERB":     {POS: "VERB"}
}


# Stop words are retrieved from http://www.damienvanholten.com/downloads/dutch-stop-words.txt

STOP_WORDS = set("""
aan af al alles als altijd andere

ben bij

daar dan dat de der deze die dit doch doen door dus

een eens en er

ge geen geweest

haar had heb hebben heeft hem het hier hij hoe hun

iemand iets ik in is

ja je

kan kon kunnen

maar me meer men met mij mijn moet

na naar niet niets nog nu

of om omdat ons ook op over

reeds

te tegen toch toen tot

u uit uw

van veel voor

want waren was wat we wel werd wezen wie wij wil worden

zal ze zei zelf zich zij zijn zo zonder zou
""".split())


# TODO Make tokenizer excpetions for Dutch

TOKENIZER_EXCEPTIONS = {

}


ORTH_ONLY = {

}
