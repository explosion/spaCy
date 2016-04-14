from .util import set_lang_class, get_lang_class, get_package, get_package_by_name

from . import en
from . import de


set_lang_class(en.English.lang, en.English)
set_lang_class(de.German.lang, de.German)


def load(name, vectors=None, via=None):
    package = get_package_by_name(name, via=via)
    vectors_package = get_package_by_name(vectors, via=via)
    cls = get_lang_class(name)
    return cls(package=package, vectors_package=vectors_package)
