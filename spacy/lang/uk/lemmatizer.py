# coding: utf8
from __future__ import unicode_literals

from ..ru.lemmatizer import RussianLemmatizer


class UkrainianLemmatizer(RussianLemmatizer):
    def __init__(self, pymorphy2_lang="ru"):
        try:
            super(UkrainianLemmatizer, self).__init__(pymorphy2_lang="uk")
        except ImportError:
            raise ImportError(
                "The Ukrainian lemmatizer requires the pymorphy2 library and dictionaries: "
                'try to fix it with "pip install git+https://github.com/kmike/pymorphy2.git pymorphy2-dicts-uk"'
            )
