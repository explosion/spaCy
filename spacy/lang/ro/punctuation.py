# coding: utf8
from __future__ import unicode_literals

import itertools

from ..char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, LIST_CURRENCY
from ..char_classes import LIST_ICONS, CURRENCY
from ..char_classes import CONCAT_QUOTES, ALPHA_LOWER, ALPHA_UPPER, ALPHA, PUNCT


_list_icons = [x for x in LIST_ICONS if x != "°"]
_list_icons = [x.replace("\\u00B0", "") for x in _list_icons]


_ro_variants = {
    "Ă": ["Ă", "A"],
    "Â": ["Â", "A"],
    "Î": ["Î", "I"],
    "Ș": ["Ș", "Ş", "S"],
    "Ț": ["Ț", "Ţ", "T"],
}


def _make_ro_variants(tokens):
    variants = []
    for token in tokens:
        upper_token = token.upper()
        upper_char_variants = [_ro_variants.get(c, [c]) for c in upper_token]
        upper_variants = ["".join(x) for x in itertools.product(*upper_char_variants)]
        for variant in upper_variants:
            variants.extend([variant, variant.lower(), variant.title()])
    return sorted(list(set(variants)))


# UD_Romanian-RRT closed class prefixes
# POS: ADP|AUX|CCONJ|DET|NUM|PART|PRON|SCONJ
_ud_rrt_prefixes = [
    "a-",
    "c-",
    "ce-",
    "cu-",
    "d-",
    "de-",
    "dintr-",
    "e-",
    "făr-",
    "i-",
    "l-",
    "le-",
    "m-",
    "mi-",
    "n-",
    "ne-",
    "p-",
    "pe-",
    "prim-",
    "printr-",
    "s-",
    "se-",
    "te-",
    "v-",
    "într-",
    "ș-",
    "și-",
    "ți-",
]
_ud_rrt_prefix_variants = _make_ro_variants(_ud_rrt_prefixes)


# UD_Romanian-RRT closed class suffixes without NUM
# POS: ADP|AUX|CCONJ|DET|PART|PRON|SCONJ
_ud_rrt_suffixes = [
    "-a",
    "-aceasta",
    "-ai",
    "-al",
    "-ale",
    "-alta",
    "-am",
    "-ar",
    "-astea",
    "-atâta",
    "-au",
    "-aș",
    "-ați",
    "-i",
    "-ilor",
    "-l",
    "-le",
    "-lea",
    "-mea",
    "-meu",
    "-mi",
    "-mă",
    "-n",
    "-ndărătul",
    "-ne",
    "-o",
    "-oi",
    "-or",
    "-s",
    "-se",
    "-si",
    "-te",
    "-ul",
    "-ului",
    "-un",
    "-uri",
    "-urile",
    "-urilor",
    "-veți",
    "-vă",
    "-ăștia",
    "-și",
    "-ți",
]
_ud_rrt_suffix_variants = _make_ro_variants(_ud_rrt_suffixes)


_prefixes = (
    ["§", "%", "=", "—", "–", r"\+(?![0-9])"]
    + _ud_rrt_prefix_variants
    + LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_CURRENCY
    + LIST_ICONS
)


_suffixes = (
    _ud_rrt_suffix_variants
    + LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + _list_icons
    + ["—", "–"]
    + [
        r"(?<=[0-9])\+",
        r"(?<=°[FfCcKk])\.",
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9{al}{e}{p}(?:{q})])\.".format(
            al=ALPHA_LOWER, e=r"%²\-\+", q=CONCAT_QUOTES, p=PUNCT
        ),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
    ]
)

_infixes = (
    LIST_ELLIPSES
    + _list_icons
    + [
        r"(?<=[0-9])[+\*^](?=[0-9-])",
        r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
            al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
        ),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}0-9])[:<>=](?=[{a}])".format(a=ALPHA),
    ]
)

TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
