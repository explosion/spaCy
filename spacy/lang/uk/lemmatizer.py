from typing import Optional

from thinc.api import Model

from ..ru.lemmatizer import RussianLemmatizer
from ...lookups import Lookups
from ...vocab import Vocab


class UkrainianLemmatizer(RussianLemmatizer):
    def __init__(
        self,
        vocab: Vocab,
        model: Optional[Model],
        name: str = "lemmatizer",
        *,
        mode: str = "pymorphy2",
        lookups: Optional[Lookups] = None,
    ) -> None:
        super().__init__(vocab, model, name, mode=mode, lookups=lookups)
        try:
            from pymorphy2 import MorphAnalyzer
        except ImportError:
            raise ImportError(
                "The Ukrainian lemmatizer requires the pymorphy2 library and "
                'dictionaries: try to fix it with "pip uninstall pymorphy2" and'
                '"pip install git+https://github.com/kmike/pymorphy2.git pymorphy2-dicts-uk"'
            ) from None
        if UkrainianLemmatizer._morph is None:
            UkrainianLemmatizer._morph = MorphAnalyzer(lang="uk")
