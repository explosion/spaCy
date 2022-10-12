from typing import Optional, Callable

from thinc.api import Model

from ...pipeline.lemmatizer import lemmatizer_score, PyMorhpy2Lemmatizer
from ...vocab import Vocab


class UkrainianLemmatizer(PyMorhpy2Lemmatizer):
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
            vocab, model, "uk", name=name, mode=mode, overwrite=overwrite, scorer=scorer, 
        )
