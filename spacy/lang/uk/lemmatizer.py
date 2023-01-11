from typing import Optional, Callable

from thinc.api import Model

from ..ru.lemmatizer import RussianLemmatizer
from ...pipeline.lemmatizer import lemmatizer_score
from ...vocab import Vocab


class UkrainianLemmatizer(RussianLemmatizer):
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
        if mode in {"pymorphy2", "pymorphy2_lookup"}:
            try:
                from pymorphy2 import MorphAnalyzer
            except ImportError:
                raise ImportError(
                    "The Ukrainian lemmatizer mode 'pymorphy2' requires the "
                    "pymorphy2 library and dictionaries. Install them with: "
                    "pip install pymorphy2 pymorphy2-dicts-uk"
                ) from None
            if getattr(self, "_morph", None) is None:
                self._morph = MorphAnalyzer(lang="uk")
        elif mode in {"pymorphy3", "pymorphy3_lookup"}:
            try:
                from pymorphy3 import MorphAnalyzer
            except ImportError:
                raise ImportError(
                    "The Ukrainian lemmatizer mode 'pymorphy3' requires the "
                    "pymorphy3 library and dictionaries. Install them with: "
                    "pip install pymorphy3 pymorphy3-dicts-uk"
                ) from None
            if getattr(self, "_morph", None) is None:
                self._morph = MorphAnalyzer(lang="uk")
        super().__init__(
            vocab, model, name, mode=mode, overwrite=overwrite, scorer=scorer
        )
