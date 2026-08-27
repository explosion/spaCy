from ..punctuation import (
    TOKENIZER_INFIXES as BASE_TOKENIZER_INFIXES,
    TOKENIZER_PREFIXES as BASE_TOKENIZER_PREFIXES,
    TOKENIZER_SUFFIXES as BASE_TOKENIZER_SUFFIXES,
)

_prefixes = [r"\w{1,3}\$"] + BASE_TOKENIZER_PREFIXES

_suffixes = BASE_TOKENIZER_SUFFIXES
# Only up to 64 to prevent quadratic backtracking
_infixes = [r"(\w{1,64}-\w{1,64}(-\w{1,64})*)"] + BASE_TOKENIZER_INFIXES

TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes
