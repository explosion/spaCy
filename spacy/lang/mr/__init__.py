from ...language import Language, BaseDefaults


class MarathiDefaults(BaseDefaults):
    pass


class Marathi(Language):
    lang = "mr"
    Defaults = MarathiDefaults


__all__ = ["Marathi"]
