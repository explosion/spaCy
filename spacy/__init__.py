import pathlib

from .util import set_lang_class, get_lang_class

from . import en
from . import de
from . import zh


try:
    basestring
except NameError:
    basestring = str



set_lang_class(en.English.lang, en.English)
set_lang_class(de.German.lang, de.German)
set_lang_class(zh.Chinese.lang, zh.Chinese)


def load(name, **overrides):
    target_name, target_version = util.split_data_name(name)
    path = overrides.get('path', util.get_data_path())
    path = util.match_best_version(target_name, target_version, path)

    if isinstance(overrides.get('vectors'), basestring):
        vectors = util.match_best_version(overrides.get('vectors'), None, path)
    
    cls = get_lang_class(target_name)
    return cls(path=path, **overrides)
