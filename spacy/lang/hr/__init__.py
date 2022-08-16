from ...language import Language, BaseDefaults


class CroatianDefaults(BaseDefaults):
    pass


class Croatian(Language):
    lang = "hr"
    Defaults = CroatianDefaults


__all__ = ["Croatian"]
