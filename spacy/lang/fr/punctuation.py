from ..char_classes import (
    ALPHA,
    ALPHA_LOWER,
    ALPHA_UPPER,
    CONCAT_QUOTES,
    CURRENCY,
    LIST_ELLIPSES,
    LIST_ICONS,
    LIST_PUNCT,
    LIST_QUOTES,
    UNITS,
)

ELISION = " ' ` ´ ’ ".replace(" ", "")
HYPHENS = r"- – — ‐ ‑".replace(" ", "")

# fmt: off
_suffix_inversion = [
    "je", "tu", "on", "il", "elle", "iel",
    "nous", "vous", "elles", "ils", "iels",
    "moi", "toi", "lui", "leur", "eux", "elleux",
    "ce", "ici", "là",
    # to avoid matching: Villar-le-bois
    fr"la(?![{HYPHENS}])",
    fr"le(?![{HYPHENS}])",
    fr"les(?![{HYPHENS}])",
    fr"en(?![{HYPHENS}])", "y",
    # a-t-on, a-t'on
    fr"t[{HYPHENS}]??[{ELISION}]?",
    fr"m[{ELISION}]?",
]
_prefix_elision = [
    "n", "s", "c", "d", "j", "m", "t", "l", "qu",
    # i exclude "quelqu'un"/"quelqu'un" because it's one token (and not quelque + un, which would lacks the idea of 'one person').
    fr"quelqu(?![{ELISION}]un[ex]*\b)",
    "jusqu", "presqu", "lorsqu", "puisqu", "quoiqu",
]
# fmt: on


def upperandtitle(a):
    """[alors, on] -> [alors, Alors, ALORS, on, On, ON]"""

    def fn(i):
        t = i[0].upper() + i[1:]
        u = i.upper()
        return [i, t] if t == u else [i, t, u]

    return [x for y in [fn(i) for i in a] for x in y]


_elision = rf"(?:\b(?:{r'|'.join(upperandtitle(_prefix_elision))})[{ELISION}])"
_inversion = (
    rf"(?:(?<=[^\W\d])[{HYPHENS}]\b(?:{r'|'.join(upperandtitle(_suffix_inversion))})\b)"
)

TOKENIZER_PREFIXES = [_elision]

TOKENIZER_INFIXES = (
    # base list without hyphen regex
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
            al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
        ),
        # r"(?<=[0-9])[+\-\*^](?=[0-9-])",
        # "2024-12-20" should be one token, so i remove "\-" from the above default regex
        r"(?<=[0-9])[+\*^](?=[0-9-])",
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=\d),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}]),(?=[\d])".format(a=ALPHA),
        r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
    ]
    # conditionnal hyphen: verb-subject inversion
    + [_inversion]
)

TOKENIZER_SUFFIXES = (
    # base list, les hyphens and english things such as "'s"
    LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_ICONS
    + [
        r"(?<=[0-9])\+",
        r"(?<=°[FfCcKk])\.",  # °C. -> ["°C", "."]
        r"(?<=[0-9])%",  # 4% -> ["4", "%"]
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=UNITS),
        r"(?<=[0-9{al}{e}(?:{q})])\.".format(
            al=ALPHA_LOWER, e=r"%²\-\+", q=CONCAT_QUOTES
        ),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
    ]
)
