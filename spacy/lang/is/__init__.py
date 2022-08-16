from ...language import Language, BaseDefaults


class IcelandicDefaults(BaseDefaults):
    pass


class Icelandic(Language):
    lang = "is"
    Defaults = IcelandicDefaults


__all__ = ["Icelandic"]
