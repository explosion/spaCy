from typing import Optional, Callable

from thinc.api import Model

from ...pipeline.lemmatizer import lemmatizer_score
from ...pipeline.pymorphy_lemmatizer import PyMorhpyLemmatizer
from ...vocab import Vocab


class UkrainianLemmatizer(PyMorhpyLemmatizer):
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
            vocab, model, "uk", name=name, mode=mode, overwrite=overwrite, scorer=scorer, 
        )
