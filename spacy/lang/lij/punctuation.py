from ..char_classes import ALPHA
from ..punctuation import TOKENIZER_INFIXES

ELISION = " ' ’ ".strip().replace(" ", "").replace("\n", "")


_infixes = TOKENIZER_INFIXES + [
    r"(?<=[{a}][{el}])(?=[{a}])".format(a=ALPHA, el=ELISION)
]

TOKENIZER_INFIXES = _infixes
