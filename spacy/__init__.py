from . import util
from .en import English


def load(name, vectors=None, via=None):
    return English(
        package=util.get_package_by_name(name, via=via),
        vectors_package=util.get_package_by_name(vectors, via=via))
