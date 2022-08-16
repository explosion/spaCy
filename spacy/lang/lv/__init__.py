from ...language import Language, BaseDefaults


class LatvianDefaults(BaseDefaults):
    pass


class Latvian(Language):
    lang = "lv"
    Defaults = LatvianDefaults


__all__ = ["Latvian"]
