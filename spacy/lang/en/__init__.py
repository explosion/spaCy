# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .morph_rules import MORPH_RULES
from .syntax_iterators import SYNTAX_ITERATORS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG
from ...util import update_exc


def _return_en(_):
    return "en"


class EnglishDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = _return_en
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    tag_map = TAG_MAP
    stop_words = STOP_WORDS
    morph_rules = MORPH_RULES
    syntax_iterators = SYNTAX_ITERATORS
    single_orth_variants = [
        {"tags": ["NFP"], "variants": ["…", "..."]},
        {"tags": [":"], "variants": ["-", "—", "–", "--", "---", "——"]},
    ]
    paired_orth_variants = [
        {"tags": ["``", "''"], "variants": [("'", "'"), ("‘", "’")]},
        {"tags": ["``", "''"], "variants": [('"', '"'), ("“", "”")]},
    ]

    @classmethod
    def is_base_form(cls, univ_pos, morphology=None):
        """
        Check whether we're dealing with an uninflected paradigm, so we can
        avoid lemmatization entirely.

        univ_pos (unicode / int): The token's universal part-of-speech tag.
        morphology (dict): The token's morphological features following the
            Universal Dependencies scheme.
        """
        if morphology is None:
            morphology = {}
        if univ_pos == "noun" and morphology.get("Number") == "sing":
            return True
        elif univ_pos == "verb" and morphology.get("VerbForm") == "inf":
            return True
        # This maps 'VBP' to base form -- probably just need 'IS_BASE'
        # morphology
        elif univ_pos == "verb" and (
            morphology.get("VerbForm") == "fin"
            and morphology.get("Tense") == "pres"
            and morphology.get("Number") is None
        ):
            return True
        elif univ_pos == "adj" and morphology.get("Degree") == "pos":
            return True
        elif morphology.get("VerbForm") == "inf":
            return True
        elif morphology.get("VerbForm") == "none":
            return True
        elif morphology.get("Degree") == "pos":
            return True
        else:
            return False


class English(Language):
    lang = "en"
    Defaults = EnglishDefaults


__all__ = ["English"]
