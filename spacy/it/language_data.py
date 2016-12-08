# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import TOKENIZER_PREFIXES
from ..language_data import TOKENIZER_SUFFIXES
from ..language_data import TOKENIZER_INFIXES


def strings_to_exc(orths):
    return {orth: [{ORTH: orth}] for orth in orths}


PRON_LEMMA = "-PRON-"


TAG_MAP = {

}

STOP_WORDS = set("""

""".split())


TOKENIZER_EXCEPTIONS = {

}


ORTH_ONLY = {

}
