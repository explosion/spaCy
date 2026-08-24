# cython: profile=False
IDS = {
    "": NO_TAG,
    "ADJ": ADJ,
    "ADP": ADP,
    "ADV": ADV,
    "AUX": AUX,
    "CONJ": CONJ,  # U20
    "CCONJ": CCONJ,
    "DET": DET,
    "INTJ": INTJ,
    "NOUN": NOUN,
    "NUM": NUM,
    "PART": PART,
    "PRON": PRON,
    "PROPN": PROPN,
    "PUNCT": PUNCT,
    "SCONJ": SCONJ,
    "SYM": SYM,
    "VERB": VERB,
    "X": X,
    "EOL": EOL,
    "SPACE": SPACE
}

# Make these ints in Python, so that we don't get this unexpected 'flag' type
# This will match the behaviour before Cython 3
IDS = {name: int(value) for name, value in IDS.items()}
NAMES = {value: key for key, value in IDS.items()}

# As of Cython 3.1, the global Python namespace no longer has the enum
# contents by default.
globals().update(IDS)

