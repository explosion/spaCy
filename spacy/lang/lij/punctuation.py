from ..punctuation import (
    TOKENIZER_PREFIXES as BASE_TOKENIZER_PREFIXES,
    TOKENIZER_INFIXES as BASE_TOKENIZER_INFIXES,
)
from ..char_classes import ALPHA


ELISION = "'’"


_prefixes = [
    r"['’‘][0-9]{2}",  # shorthand for years
    r"[0-9]+°(?![cfkCFK])",  # use of degree symbol as ordinal indicator
    r"[{el}‘]nn?[{el}]?".format(el=ELISION),  # elided forms of "un(na)"
] + BASE_TOKENIZER_PREFIXES


_infixes = BASE_TOKENIZER_INFIXES + [
    r"(?<=[{a}][{el}])(?=[{a}0-9\"])".format(a=ALPHA, el=ELISION),
]

TOKENIZER_PREFIXES = _prefixes
TOKENIZER_INFIXES = _infixes
