from ..char_classes import (
    ALPHA,
    ALPHA_LOWER,
    ALPHA_UPPER,
    CONCAT_QUOTES,
    HYPHENS,
    LIST_ELLIPSES,
    LIST_ICONS,
    LIST_PUNCT,
    LIST_QUOTES,
    merge_chars,
)

ELISION = "'’".replace(" ", "")

_prefixes_elision = "m n l y t k w"
_prefixes_elision += " " + _prefixes_elision.upper()

TOKENIZER_PREFIXES = (
    LIST_PUNCT
    + LIST_QUOTES
    + [
        r"(?:({pe})[{el}])(?=[{a}])".format(
            a=ALPHA, el=ELISION, pe=merge_chars(_prefixes_elision)
        )
    ]
)

TOKENIZER_SUFFIXES = (
    LIST_PUNCT
    + LIST_QUOTES
    + LIST_ELLIPSES
    + [
        r"(?<=[0-9])%",  # numbers like 10%
        r"(?<=[0-9])(?:{h})".format(h=HYPHENS),  # hyphens after numbers
        r"(?<=[{a}])['’]".format(a=ALPHA),  # apostrophes after letters
        r"(?<=[{a}])['’][mwlnytk](?=\s|$)".format(a=ALPHA),  # contractions
        r"(?<=[{a}0-9])\)",  # right parenthesis after letter/number
        r"(?<=[{a}])\.(?=\s|$)".format(
            a=ALPHA
        ),  # period after letter if space or end of string
        r"(?<=\))[\.\?!]",  # punctuation immediately after right parenthesis
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
        r"(?<=[{a}0-9])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
        r"(?<=[{a}][{el}])(?=[{a}])".format(a=ALPHA, el=ELISION),
    ]
)
