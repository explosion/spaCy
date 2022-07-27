class LatinDefaults(BaseDefaults):
    pass

class Latin(Language):
    lang = "la"
    Defaults = LatinDefaults


__all__ = ["Latin"]
