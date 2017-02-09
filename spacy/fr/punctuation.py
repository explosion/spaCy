# encoding: utf8

from __future__ import unicode_literals

from ..language_data.punctuation import ALPHA, TOKENIZER_INFIXES


_ELISION = " ' ’ "
ELISION = _ELISION.strip().replace(' ', '').replace('\n', '')

TOKENIZER_INFIXES += [
    r'(?<=[{a}][{el}])(?=[{a}])'.format(a=ALPHA, el=ELISION),
]


__all__ = ["TOKENIZER_SUFFIXES", "TOKENIZER_INFIXES"]
