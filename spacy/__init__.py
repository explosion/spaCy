from . import util
from .en import English


def load(name, via=None, vectors_name=None):
    package = util.get_package_by_name(name, via=via)
    vectors_package = util.get_package_by_name(vectors_name, via=via)
    return English(package=package, vectors_package=vectors_package)
