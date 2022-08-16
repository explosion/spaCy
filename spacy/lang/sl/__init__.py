from ...language import Language, BaseDefaults


class SlovenianDefaults(BaseDefaults):
    pass


class Slovenian(Language):
    lang = "sl"
    Defaults = SlovenianDefaults


__all__ = ["Slovenian"]
