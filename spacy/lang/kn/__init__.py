from ...language import Language, BaseDefaults


class KannadaDefaults(BaseDefaults):
    pass


class Kannada(Language):
    lang = "kn"
    Defaults = KannadaDefaults


__all__ = ["Kannada"]
