from ...language import Language, BaseDefaults


class EstonianDefaults(BaseDefaults):
    pass


class Estonian(Language):
    lang = "et"
    Defaults = EstonianDefaults


__all__ = ["Estonian"]
