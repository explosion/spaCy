from . import util
from .en import English


def load(name, via=None):
    package = util.get_package_by_name(name, via=via)
    return English(package)
