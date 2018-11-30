# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS

# uncomment if files are available
# from .norm_exceptions import NORM_EXCEPTIONS
# from .tag_map import TAG_MAP
# from .morph_rules import MORPH_RULES

# uncomment if lookup-based lemmatizer is available
from .lemmatizer import LOOKUP

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups

# Create a Language subclass
# Documentation: https://spacy.io/docs/usage/adding-languages

# This file should be placed in spacy/lang/ca (ISO code of language).
# Before submitting a pull request, make sure the remove all comments from the
# language data files, and run at least the basic tokenizer tests. Simply add the
# language ID to the list of languages in spacy/tests/conftest.py to include it
# in the basic tokenizer sanity tests. You can optionally add a fixture for the
# language's tokenizer and add more specific tests. For more info, see the
# tests documentation: https://github.com/explosion/spaCy/tree/master/spacy/tests


class CatalanDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'ca' # ISO code
    # add more norm exception dictionaries here
    lex_attr_getters[NORM] = add_lookups(Language.Defaults.lex_attr_getters[NORM], BASE_NORMS)

    # overwrite functions for lexical attributes
    lex_attr_getters.update(LEX_ATTRS)

    # add custom tokenizer exceptions to base exceptions
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)

    # add stop words
    stop_words = STOP_WORDS

    # if available: add tag map
    # tag_map = dict(TAG_MAP)

    # if available: add morph rules
    # morph_rules = dict(MORPH_RULES)

    lemma_lookup = LOOKUP


class Catalan(Language):
    lang = 'ca' # ISO code
    Defaults = CatalanDefaults # set Defaults to custom language defaults


# set default export – this allows the language class to be lazy-loaded
__all__ = ['Catalan']
