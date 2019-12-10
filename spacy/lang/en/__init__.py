# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .norm_exceptions import NORM_EXCEPTIONS
from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .morph_rules import MORPH_RULES
from .syntax_iterators import SYNTAX_ITERATORS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


def _return_en(_):
    return "en"


class EnglishDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = _return_en
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS, NORM_EXCEPTIONS
    )
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


class English(Language):
    lang = "en"
    Defaults = EnglishDefaults


__all__ = ["English"]
