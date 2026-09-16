from ..char_classes import ALPHA, ALPHA_UPPER, CURRENCY, UNITS
from ..punctuation import TOKENIZER_INFIXES, TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES

# ASCII plus Arabic-Indic and Eastern Arabic-Indic digits.
_NUMERIC = r"0-9\u0660-\u0669\u06F0-\u06F9"
_URDU_PUNCT = "۔؟،؛"
# Harakat / tanween / superscript alef. Latin COMBINING_DIACRITICS is U+0300–036F.
_ARABIC_MARKS = r"\u064b-\u065f\u0670"
_URDU_ELLIPSES = [r"۔۔+"]

TOKENIZER_SUFFIXES = (
    list(TOKENIZER_SUFFIXES)
    + _URDU_ELLIPSES
    + [
        r"(?<=[{n}])\+".format(n=_NUMERIC),
        r"(?<=[{n}])%".format(n=_NUMERIC),
        r"(?<=[{n}])٪".format(n=_NUMERIC),
        r"(?<=[{n}])(?:{c})".format(n=_NUMERIC, c=CURRENCY),
        r"(?<=[{n}])(?:{u})".format(n=_NUMERIC, u=UNITS),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
    ]
)

TOKENIZER_PREFIXES = list(TOKENIZER_PREFIXES) + _URDU_ELLIPSES

TOKENIZER_INFIXES = (
    list(TOKENIZER_INFIXES)
    + _URDU_ELLIPSES
    + [
        r"(?<=[{a}])[{p}](?=[{a}])".format(a=ALPHA, p=_URDU_PUNCT),
        r"(?<=[{d}])[{p}](?=[{a}])".format(d=_ARABIC_MARKS, p=_URDU_PUNCT, a=ALPHA),
        r"(?<=[{n}])،(?=[{n}])".format(n=_NUMERIC),
        r"(?<=[{n}])[+\-*^](?=[{n}-])".format(n=_NUMERIC),
    ]
)
