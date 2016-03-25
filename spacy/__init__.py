from . import util

from .en import English
from .de import German


util.register_lang(English.lang, English)
util.register_lang(German.lang, German)


def load(name, vectors=None, via=None):
    package = util.get_package_by_name(name, via=via)
    vectors_package = util.get_package_by_name(vectors, via=via)
    cls = util.get_lang(name)
    return cls(package=package, vectors_package=vectors_package)
