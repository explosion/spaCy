from ...language import Language, BaseDefaults


class GujaratiDefaults(BaseDefaults):
    pass


class Gujarati(Language):
    lang = "gu"
    Defaults = GujaratiDefaults


__all__ = ["Gujarati"]
