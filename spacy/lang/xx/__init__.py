from thinc.api import Config

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language


DEFAULT_CONFIG = """
[nlp]
lang = "xx"
"""


class MultiLanguageDefaults(Language.Defaults):
    tokenizer_exceptions = BASE_EXCEPTIONS


class MultiLanguage(Language):
    """Language class to be used for models that support multiple languages.
    This module allows models to specify their language ID as 'xx'.
    """

    lang = "xx"
    Defaults = MultiLanguageDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["MultiLanguage"]
