from . import util
from .about import __models__
import importlib


def load(name, vectors=None, via=None):
    if name not in __models__:
        raise Exception('Model %s not found.' % name)

    mod = importlib.import_module('.%s' % __models__[name]['module'], 'spacy')
    return getattr(mod, __models__[name]['class'])(
        package=util.get_package_by_name(name, via=via),
        vectors_package=util.get_package_by_name(vectors, via=via))
