from ...language import Language, BaseDefaults


class AfrikaansDefaults(BaseDefaults):
    pass


class Afrikaans(Language):
    lang = "af"
    Defaults = AfrikaansDefaults


__all__ = ["Afrikaans"]
