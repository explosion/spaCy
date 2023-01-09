from ..char_classes import LIST_ELLIPSES, LIST_ICONS
from ..char_classes import CONCAT_QUOTES, ALPHA, ALPHA_LOWER, ALPHA_UPPER
from ..punctuation import TOKENIZER_SUFFIXES


_quotes = CONCAT_QUOTES.replace("'", "")

_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[{al}])\.(?=[{au}])".format(al=ALPHA_LOWER, au=ALPHA_UPPER),
        r"(?<=[{a}])[,!?](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])[:<>=](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])([{q}\)\]\(\[])(?=[{a}])".format(a=ALPHA, q=_quotes),
        r"(?<=[{a}])--(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
    ]
)

_suffixes = [
    suffix
    for suffix in TOKENIZER_SUFFIXES
    if suffix not in ["'s", "'S", "’s", "’S", r"\'"]
]
_suffixes += [r"(?<=[^sSxXzZ])\'"]


TOKENIZER_INFIXES = _infixes
TOKENIZER_SUFFIXES = _suffixes
