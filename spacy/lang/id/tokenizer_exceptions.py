# coding: utf8
from __future__ import unicode_literals

import regex as re

from ._tokenizer_exceptions_list import ID_BASE_EXCEPTIONS
from ..tokenizer_exceptions import URL_PATTERN
from ...symbols import ORTH


_exc = {}

for orth in ID_BASE_EXCEPTIONS:
    _exc[orth] = [{ORTH: orth}]

    orth_title = orth.title()
    _exc[orth_title] = [{ORTH: orth_title}]

    orth_caps = orth.upper()
    _exc[orth_caps] = [{ORTH: orth_caps}]

    orth_lower = orth.lower()
    _exc[orth_lower] = [{ORTH: orth_lower}]

    if '-' in orth:
        orth_title = '-'.join([part.title() for part in orth.split('-')])
        _exc[orth_title] = [{ORTH: orth_title}]

        orth_caps = '-'.join([part.upper() for part in orth.split('-')])
        _exc[orth_caps] = [{ORTH: orth_caps}]


_hyphen_prefix = """abdur abdus abou aboul abror abshar abu abubakar abul
aero agri agro ahmadi ahmed air abd abdel abdul ad adz afro al ala ali all
amir an antar anti ar as ash asy at ath az bekas ber best bi co di double
dual duo e eco eks el era ex full hi high i in inter intra ke kontra korona
kuartal lintas m macro makro me mem meng micro mid mikro mini multi neo nge
no non on pan pasca pe pem poli poly post pra pre pro re se self serba seri
sub super t trans u ultra un x \#""".split()

_hyphen_infix = """ber-an berke-an de-isasi di-kan di-kannya di-nya ke-an
ke-annya me-kan me-kannya men-kan men-kannya meng-kannya pe-an pen-an
per-an per-i se-an se-nya ter-i ter-kan ter-kannya""".split()

_hyphen_suffix = """el"""

_regular_exp = ['^{p}-[A-Za-z0-9]+$'.format(p=prefix) for prefix in _hyphen_prefix]
_regular_exp += ['^{0}-[A-Za-z0-9]+-{1}$'.format(*infix.split('-')) for infix in _hyphen_infix]
_regular_exp += ['^[A-Za-z0-9]+-{s}$'.format(s=suffix) for suffix in _hyphen_suffix]
_regular_exp.append(URL_PATTERN)

TOKENIZER_EXCEPTIONS = dict(_exc)
TOKEN_MATCH = re.compile('|'.join('(?:{})'.format(m) for m in _regular_exp), re.IGNORECASE).match
