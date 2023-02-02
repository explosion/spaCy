from ...language import Language


class MultiLanguage(Language):
    """Language class to be used for models that support multiple languages.
    This module allows models to specify their language ID as 'mul'.
    """

    lang = "mul"


__all__ = ["MultiLanguage"]
