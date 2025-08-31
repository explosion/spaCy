from spacy.symbols import NORM, ORTH


def make_variants(base, first_norm, second_orth, second_norm):
    return {
        base: [
            {ORTH: base.split("'")[0] + "'", NORM: first_norm},
            {ORTH: second_orth, NORM: second_norm},
        ],
        base.capitalize(): [
            {
                ORTH: base.split("'")[0].capitalize() + "'",
                NORM: first_norm.capitalize(),
            },
            {ORTH: second_orth, NORM: second_norm},
        ],
    }


TOKENIZER_EXCEPTIONS = {"Dr.": [{ORTH: "Dr."}]}

# Apostrophe forms
TOKENIZER_EXCEPTIONS.update(make_variants("m'ap", "mwen", "ap", "ap"))
TOKENIZER_EXCEPTIONS.update(make_variants("n'ap", "nou", "ap", "ap"))
TOKENIZER_EXCEPTIONS.update(make_variants("l'ap", "li", "ap", "ap"))
TOKENIZER_EXCEPTIONS.update(make_variants("y'ap", "yo", "ap", "ap"))
TOKENIZER_EXCEPTIONS.update(make_variants("m'te", "mwen", "te", "te"))
TOKENIZER_EXCEPTIONS.update(make_variants("m'pral", "mwen", "pral", "pral"))
TOKENIZER_EXCEPTIONS.update(make_variants("w'ap", "ou", "ap", "ap"))
TOKENIZER_EXCEPTIONS.update(make_variants("k'ap", "ki", "ap", "ap"))
TOKENIZER_EXCEPTIONS.update(make_variants("p'ap", "pa", "ap", "ap"))
TOKENIZER_EXCEPTIONS.update(make_variants("t'ap", "te", "ap", "ap"))

# Non-apostrophe contractions (with capitalized variants)
TOKENIZER_EXCEPTIONS.update(
    {
        "map": [
            {ORTH: "m", NORM: "mwen"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "Map": [
            {ORTH: "M", NORM: "Mwen"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "lem": [
            {ORTH: "le", NORM: "le"},
            {ORTH: "m", NORM: "mwen"},
        ],
        "Lem": [
            {ORTH: "Le", NORM: "Le"},
            {ORTH: "m", NORM: "mwen"},
        ],
        "lew": [
            {ORTH: "le", NORM: "le"},
            {ORTH: "w", NORM: "ou"},
        ],
        "Lew": [
            {ORTH: "Le", NORM: "Le"},
            {ORTH: "w", NORM: "ou"},
        ],
        "nap": [
            {ORTH: "n", NORM: "nou"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "Nap": [
            {ORTH: "N", NORM: "Nou"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "lap": [
            {ORTH: "l", NORM: "li"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "Lap": [
            {ORTH: "L", NORM: "Li"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "yap": [
            {ORTH: "y", NORM: "yo"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "Yap": [
            {ORTH: "Y", NORM: "Yo"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "mte": [
            {ORTH: "m", NORM: "mwen"},
            {ORTH: "te", NORM: "te"},
        ],
        "Mte": [
            {ORTH: "M", NORM: "Mwen"},
            {ORTH: "te", NORM: "te"},
        ],
        "mpral": [
            {ORTH: "m", NORM: "mwen"},
            {ORTH: "pral", NORM: "pral"},
        ],
        "Mpral": [
            {ORTH: "M", NORM: "Mwen"},
            {ORTH: "pral", NORM: "pral"},
        ],
        "wap": [
            {ORTH: "w", NORM: "ou"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "Wap": [
            {ORTH: "W", NORM: "Ou"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "kap": [
            {ORTH: "k", NORM: "ki"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "Kap": [
            {ORTH: "K", NORM: "Ki"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "tap": [
            {ORTH: "t", NORM: "te"},
            {ORTH: "ap", NORM: "ap"},
        ],
        "Tap": [
            {ORTH: "T", NORM: "Te"},
            {ORTH: "ap", NORM: "ap"},
        ],
    }
)
