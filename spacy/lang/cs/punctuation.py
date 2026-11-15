from ..char_classes import ALPHA, ALPHA_UPPER
from ..punctuation import TOKENIZER_INFIXES as BASE_TOKENIZER_INFIXES
from ..punctuation import TOKENIZER_SUFFIXES as BASE_TOKENIZER_SUFFIXES

# Split off the period after a single uppercase letter ("J. Novák" ->
# "J", ".", "Novák"), as in the Czech UD treebanks.
_suffixes = BASE_TOKENIZER_SUFFIXES + [r"(?<=[{au}])\.".format(au=ALPHA_UPPER)]

# Split periods between letters ("a.s." -> "a", ".", "s", ".") but not
# between digits ("137.10").
_infixes = BASE_TOKENIZER_INFIXES + [r"(?<=[{a}])\.(?=[{a}])".format(a=ALPHA)]

TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
