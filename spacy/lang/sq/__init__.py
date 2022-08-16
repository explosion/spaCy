from ...language import Language, BaseDefaults


class AlbanianDefaults(BaseDefaults):
    pass


class Albanian(Language):
    lang = "sq"
    Defaults = AlbanianDefaults


__all__ = ["Albanian"]
