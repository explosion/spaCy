from typing import Optional, List, Dict, Tuple, Callable

from thinc.api import Model

from ...pipeline.lemmatizer import lemmatizer_score, PyMorhpy2Lemmatizer
from ...symbols import POS
from ...tokens import Token
from ...vocab import Vocab


PUNCT_RULES = {"«": '"', "»": '"'}

class RussianLemmatizer(PyMorhpy2Lemmatizer):
    def __init__(
        self,
        vocab: Vocab,
        model: Optional[Model],
        name: str = "lemmatizer",
        *,
        mode: str = "pymorphy2",
        overwrite: bool = False,
        scorer: Optional[Callable] = lemmatizer_score,
    ) -> None:
        super().__init__(
            vocab, model, "ru", name=name, mode=mode, overwrite=overwrite, scorer=scorer,
        )
