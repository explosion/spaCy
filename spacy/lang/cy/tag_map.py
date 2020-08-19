# coding: utf8
from __future__ import unicode_literals

from ...symbols import POS, PUNCT, SYM


TAG_MAP = {
    '""': {POS: PUNCT, "PunctType": "quot", "PunctSide": "fin"},
    ":": {POS: PUNCT},
    "$": {POS: SYM},
    "#": {POS: SYM},
}
