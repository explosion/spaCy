from typing import Optional

from thinc.api import Model

from ..ru.lemmatizer import RussianLemmatizer
from ...vocab import Vocab


class UkrainianLemmatizer(RussianLemmatizer):
    _morph = None

    def __init__(
        self,
        vocab: Vocab,
        model: Optional[Model],
        name: str = "lemmatizer",
        *,
        mode: str = "pymorphy2",
        overwrite: bool = False,
    ) -> None:
        if mode == "pymorphy2":
            try:
                from pymorphy2 import MorphAnalyzer
            except ImportError:
                raise ImportError(
                    "The Ukrainian lemmatizer mode 'pymorphy2' requires the "
                    "pymorphy2 library and dictionaries. Install them with: "
                    "pip install pymorphy2 pymorphy2-dicts-uk"
                ) from None
            if UkrainianLemmatizer._morph is None:
                UkrainianLemmatizer._morph = MorphAnalyzer(lang="uk")
        super().__init__(vocab, model, name, mode=mode, overwrite=overwrite)
