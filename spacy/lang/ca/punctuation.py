from ..punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES
from ..char_classes import ALPHA


ELISION = " ' ’ ".strip().replace(" ", "").replace("\n", "")


_infixes = TOKENIZER_INFIXES + [
    r"(?<=[{a}][{el}])(?=[{a}])".format(a=ALPHA, el=ELISION),
    r"('ls|'ns|'t|'m|'n|-les|-la|-lo|-los|-me|-nos|-te|-vos|-se|-hi|-ne|-ho)(?![A-Za-z])|(-l'|-n')",
]

_suffixes = TOKENIZER_SUFFIXES + [r"-"]

TOKENIZER_INFIXES = _infixes

TOKENIZER_SUFFIXES = _suffixes
