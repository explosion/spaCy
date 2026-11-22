from ..char_classes import (
    ALPHA,
    ALPHA_LOWER,
    ALPHA_UPPER,
    CONCAT_QUOTES,
    LIST_ELLIPSES,
    LIST_ICONS,
)
from ..punctuation import (
    TOKENIZER_PREFIXES as BASE_PREFIXES,
    TOKENIZER_SUFFIXES as BASE_SUFFIXES,
)

# Welsh clitics are written with an apostrophe (straight or curly) and attach
# to the preceding word ('r, 'n, 'i, 'm, 'ch, 'th, 'u, 'w) or, for f' and d',
# to the following word. They are tokenized as separate tokens, as in the UD
# Welsh treebank.
_APOSTROPHES = "'’"

_prefixes = [r"[fFdD][{ap}]".format(ap=_APOSTROPHES)]

_suffixes = [
    r"[{ap}](?:ch|th|CH|TH|[rnimuwRNIMUW])".format(ap=_APOSTROPHES),
]

# The base infixes split on a hyphen between letters. Welsh hyphenates within
# words to mark stress and to separate digraphs from letter pairs (cyd-destun
# has two Ds, cuddio one DD), so that rule is left out; the hyphen between
# digits is kept.
_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[0-9])[+\-\*^](?=[0-9-])",
        r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
            al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
        ),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
    ]
)

TOKENIZER_PREFIXES = BASE_PREFIXES + _prefixes
TOKENIZER_SUFFIXES = BASE_SUFFIXES + _suffixes
TOKENIZER_INFIXES = _infixes
