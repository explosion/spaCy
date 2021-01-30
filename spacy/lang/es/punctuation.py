from ..char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES
from ..char_classes import LIST_ICONS, CURRENCY, LIST_UNITS, PUNCT
from ..char_classes import CONCAT_QUOTES, ALPHA_LOWER, ALPHA_UPPER, ALPHA
from ..char_classes import merge_chars


_list_units = [u for u in LIST_UNITS if u != "%"]
_units = merge_chars(" ".join(_list_units))
_concat_quotes = CONCAT_QUOTES + "—–"


_suffixes = (
    ["—", "–"]
    + LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_ICONS
    + [
        r"(?<=[0-9])\+",
        r"(?<=°[FfCcKk])\.",
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=_units),
        r"(?<=[0-9{al}{e}{p}(?:{q})])\.".format(
            al=ALPHA_LOWER, e=r"%²\-\+", q=_concat_quotes, p=PUNCT
        ),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
    ]
)

_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[0-9])[+\*^](?=[0-9-])",
        r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
            al=ALPHA_LOWER, au=ALPHA_UPPER, q=_concat_quotes
        ),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
    ]
)

TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
