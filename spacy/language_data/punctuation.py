# coding: utf8
from __future__ import unicode_literals

import regex as re
re.DEFAULT_VERSION = re.VERSION1


_UNITS = """
km km² km³ m m² m³ dm dm² dm³ cm cm² cm³ mm mm² mm³ ha µm nm yd in ft kg g mg
µg t lb oz m/s km/h kmh mph hPa Pa mbar mb MB kb KB gb GB tb
TB T G M K
"""


_CURRENCY = r"""
\$ £ € ¥ ฿ US\$ C\$ A\$
"""


_QUOTES = r"""
' '' " ” “ `` ` ‘ ´ ‚ , „ » «
"""


_PUNCT = r"""
… , : ; \! \? ¿ ¡ \( \) \[ \] \{ \} < > _ # \* &
"""


_HYPHENS = r"""
- – — -- ---
"""


LIST_ELLIPSES = [
    r'\.\.+',
    "…"
]


LIST_CURRENCY = list(_CURRENCY.strip().split())
LIST_QUOTES = list(_QUOTES.strip().split())
LIST_PUNCT = list(_PUNCT.strip().split())
LIST_HYPHENS = list(_HYPHENS.strip().split())


BENGALI = r'[\p{L}&&\p{Bengali}]'
HEBREW = r'[\p{L}&&\p{Hebrew}]'
LATIN_LOWER = r'[\p{Ll}&&\p{Latin}]'
LATIN_UPPER = r'[\p{Lu}&&\p{Latin}]'
LATIN = r'[[\p{Ll}||\p{Lu}]&&\p{Latin}]'


ALPHA_LOWER = '[{}]'.format('||'.join([BENGALI, HEBREW, LATIN_LOWER]))
ALPHA_UPPER = '[{}]'.format('||'.join([BENGALI, HEBREW, LATIN_UPPER]))
ALPHA = '[{}]'.format('||'.join([BENGALI, HEBREW, LATIN]))


QUOTES = _QUOTES.strip().replace(' ', '|')
CURRENCY = _CURRENCY.strip().replace(' ', '|')
UNITS = _UNITS.strip().replace(' ', '|').replace('\n', '|')
HYPHENS = _HYPHENS.strip().replace(' ', '|')



# Prefixes

TOKENIZER_PREFIXES = (
    ['§', '%', '=', r'\+'] +
    LIST_PUNCT +
    LIST_ELLIPSES +
    LIST_QUOTES +
    LIST_CURRENCY
)


# Suffixes

TOKENIZER_SUFFIXES = (
    LIST_PUNCT +
    LIST_ELLIPSES +
    LIST_QUOTES +
    [
        r'(?<=[0-9])\+',
        r'(?<=°[FfCcKk])\.',
        r'(?<=[0-9])(?:{c})'.format(c=CURRENCY),
        r'(?<=[0-9])(?:{u})'.format(u=UNITS),
        r'(?<=[0-9{al}{p}(?:{q})])\.'.format(al=ALPHA_LOWER, p=r'%²\-\)\]\+', q=QUOTES),
        r'(?<=[{au}][{au}])\.'.format(au=ALPHA_UPPER),
        "'s", "'S", "’s", "’S"
    ]
)


# Infixes

TOKENIZER_INFIXES = (
    LIST_ELLIPSES +
    [
        r'(?<=[0-9])[+\-\*^](?=[0-9-])',
        r'(?<=[{al}])\.(?=[{au}])'.format(al=ALPHA_LOWER, au=ALPHA_UPPER),
        r'(?<=[{a}]),(?=[{a}])'.format(a=ALPHA),
        r'(?<=[{a}])[?";:=,.]*(?:{h})(?=[{a}])'.format(a=ALPHA, h=HYPHENS),
        r'(?<=[{a}"])[:<>=/](?=[{a}])'.format(a=ALPHA)
    ]
)


__all__ = ["TOKENIZER_PREFIXES", "TOKENIZER_SUFFIXES", "TOKENIZER_INFIXES"]
