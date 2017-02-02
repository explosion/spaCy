# encoding: utf8
from __future__ import unicode_literals

import re


_ALPHA_LOWER = """
a ä à á â ǎ æ ã å ā ă ą b c ç ć č ĉ ċ c̄ d ð ď e é è ê ë ė ȅ ȩ ẽ ę f g ĝ ğ h i ı
î ï í ī ì ȉ ǐ į ĩ j k ķ l ł ļ m n ñ ń ň ņ o ö ó ò ő ô õ œ ø ō ő ǒ ơ p q r ř ŗ s
ß ś š ş ŝ t ť u ú û ù ú ū ű ǔ ů ų ư v w ŵ x y ÿ ý ỳ ŷ ỹ z ź ž ż þ
"""


_ALPHA_UPPER = """
A Ä À Á Â Ǎ Æ Ã Å Ā Ă Ą B C Ç Ć Č Ĉ Ċ C̄ D Ð Ď E É È Ê Ë Ė Ȅ Ȩ Ẽ Ę F G Ĝ Ğ H I İ
Î Ï Í Ī Ì Ȉ Ǐ Į Ĩ J K Ķ L Ł Ļ M N Ñ Ń Ň Ņ O Ö Ó Ò Ő Ô Õ Œ Ø Ō Ő Ǒ Ơ P Q R Ř Ŗ S
Ś Š Ş Ŝ T Ť U Ú Û Ù Ú Ū Ű Ǔ Ů Ų Ư V W Ŵ X Y Ÿ Ý Ỳ Ŷ Ỹ Z Ź Ž Ż Þ
"""


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


ALPHA_LOWER = _ALPHA_LOWER.strip().replace(' ', '').replace('\n', '')
ALPHA_UPPER = _ALPHA_UPPER.strip().replace(' ', '').replace('\n', '')
ALPHA = ALPHA_LOWER + ALPHA_UPPER


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
        r'(?<=[{a}"])[:<>=](?=[{a}])'.format(a=ALPHA)
    ]
)


__all__ = ["TOKENIZER_PREFIXES", "TOKENIZER_SUFFIXES", "TOKENIZER_INFIXES"]
