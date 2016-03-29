from .util import set_lang_class, get_lang_class, get_package, get_package_by_name

from .en import English
from .de import German


set_lang_class(English.lang, English)
set_lang_class(German.lang, German)


def load(name, vectors=None, via=None):
    package = get_package_by_name(name, via=via)
    vectors_package = get_package_by_name(vectors, via=via)
    cls = get_lang_class(name)
    return cls(package=package, vectors_package=vectors_package)
