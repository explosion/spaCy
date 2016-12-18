# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA
from ..language_data import ENT_ID
from ..language_data import TOKENIZER_PREFIXES
from ..language_data import TOKENIZER_SUFFIXES
from ..language_data import TOKENIZER_INFIXES
from ..language_data import ENTITY_RULES, FALSE_POSITIVES

from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, ORTH_ONLY
from .lemma_rules import LEMMA_RULES
from .morph_rules import MORPH_RULES


def get_time_exc(hours):
    exc = {}
    for hour in hours:
        exc["%da.m." % hour] = [
            {ORTH: hour},
            {ORTH: "a.m."}
        ]

        exc["%dp.m." % hour] = [
            {ORTH: hour},
            {ORTH: "p.m."}
        ]

        exc["%dam" % hour] = [
            {ORTH: hour},
            {ORTH: "am", LEMMA: "a.m."}
        ]

        exc["%dpm" % hour] = [
            {ORTH: hour},
            {ORTH: "pm", LEMMA: "p.m."}
        ]
    return exc
