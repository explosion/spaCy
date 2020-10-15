from ..char_classes import LIST_ICONS, LIST_ELLIPSES
from ..char_classes import CONCAT_QUOTES, ALPHA_LOWER, ALPHA_UPPER, ALPHA
from ..char_classes import HYPHENS
from ..punctuation import TOKENIZER_SUFFIXES


_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[0-9])[+\*^](?=[0-9-])",
        r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
            al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
        ),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
        r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
    ]
)


_suffixes = ["\."] + list(TOKENIZER_SUFFIXES)


TOKENIZER_INFIXES = _infixes
TOKENIZER_SUFFIXES = _suffixes
