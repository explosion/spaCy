from typing import Optional, List, Dict, Tuple, Callable

from thinc.api import Model

from ...pipeline.lemmatizer import lemmatizer_score
from ...pipeline.pymorphy_lemmatizer import PyMorhpyLemmatizer
from ...symbols import POS
from ...tokens import Token
from ...vocab import Vocab


PUNCT_RULES = {"«": '"', "»": '"'}

class RussianLemmatizer(PyMorhpyLemmatizer):
    def __init__(
        self,
        vocab: Vocab,
        model: Optional[Model],
        name: str = "lemmatizer",
        *,
        mode: str = "pymorphy3",
        overwrite: bool = False,
        scorer: Optional[Callable] = lemmatizer_score,
    ) -> None:
        super().__init__(
            vocab, model, "ru", name=name, mode=mode, overwrite=overwrite, scorer=scorer,
        )
