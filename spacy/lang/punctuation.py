from .char_classes import LIST_PUNCT, LIST_ELLIPSES, LIST_QUOTES, LIST_CURRENCY
from .char_classes import LIST_ICONS, HYPHENS, CURRENCY, UNITS, COMBINING_DIACRITICS
from .char_classes import CONCAT_QUOTES, ALPHA_LOWER, ALPHA_UPPER, ALPHA, PUNCT


TOKENIZER_PREFIXES = (
    ["§", "%", "=", "—", "–", r"\+(?![0-9])"]
    + LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_CURRENCY
    + LIST_ICONS
)


TOKENIZER_SUFFIXES = (
    LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_ICONS
    + ["'s", "'S", "’s", "’S", "—", "–"]
    + [
        r"(?<=[0-9])\+",
        r"(?<=°[FfCcKk])\.",
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=UNITS),
        r"(?<=[0-9{al}{e}{p}(?:{q})])\.".format(
            al=ALPHA_LOWER, e=r"%²\-\+", q=CONCAT_QUOTES, p=PUNCT
        ),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
    ]
)

TOKENIZER_INFIXES = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[0-9])[+\-\*^](?=[0-9-])",
        r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
            al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
        ),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
        r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
    ]
)


# Some languages e.g. written with the Cyrillic alphabet permit the use of diacritics
# to mark stressed syllables in words where stress is distinctive. Such languages
# should use the COMBINING_DIACRITICS... suffix and infix regex lists in
# place of the standard ones.
COMBINING_DIACRITICS_TOKENIZER_SUFFIXES = list(TOKENIZER_SUFFIXES) + [
    r"(?<=[{a}][{d}])\.".format(a=ALPHA, d=COMBINING_DIACRITICS),
]

COMBINING_DIACRITICS_TOKENIZER_INFIXES = list(TOKENIZER_INFIXES) + [
    r"(?<=[{al}][{d}])\.(?=[{au}{q}])".format(
        al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES, d=COMBINING_DIACRITICS
    ),
    r"(?<=[{a}][{d}]),(?=[{a}])".format(a=ALPHA, d=COMBINING_DIACRITICS),
    r"(?<=[{a}][{d}])(?:{h})(?=[{a}])".format(
        a=ALPHA, d=COMBINING_DIACRITICS, h=HYPHENS
    ),
    r"(?<=[{a}][{d}])[:<>=/](?=[{a}])".format(a=ALPHA, d=COMBINING_DIACRITICS),
]
