# coding: utf8
from __future__ import unicode_literals

from ..char_classes import LIST_ELLIPSES, LIST_ICONS
from ..char_classes import CONCAT_QUOTES, ALPHA, ALPHA_LOWER, ALPHA_UPPER

from ..punctuation import TOKENIZER_SUFFIXES as DEFAULT_TOKENIZER_SUFFIXES


# Copied from `de` package. Main purpose is to ensure that hyphens are not
# split on.

_quotes = CONCAT_QUOTES.replace("'", '')

_infixes = (LIST_ELLIPSES + LIST_ICONS +
            [r'(?<=[{}])\.(?=[{}])'.format(ALPHA_LOWER, ALPHA_UPPER),
             r'(?<=[{a}])[,!?](?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}"])[:<>=](?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
             r'(?<=[{a}])([{q}\)\]\(\[])(?=[{a}])'.format(a=ALPHA, q=_quotes),
             r'(?<=[{a}])--(?=[{a}])'.format(a=ALPHA),
             r'(?<=[0-9])-(?=[0-9])'])


# Remove "'s" suffix from suffix list. In Dutch, "'s" is a plural ending when
# it occurs as a suffix and a clitic for "eens" in standalone use. To avoid
# ambiguity it's better to just leave it attached when it occurs as a suffix.
default_suffix_blacklist = ("'s", "'S", '’s', '’S')
_suffixes = [suffix for suffix in DEFAULT_TOKENIZER_SUFFIXES
             if suffix not in default_suffix_blacklist]

TOKENIZER_INFIXES = _infixes
TOKENIZER_SUFFIXES = _suffixes
