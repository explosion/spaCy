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
    data_path = overrides.get('path', util.get_data_path())
    if target_name == 'en' and 'add_vectors' not in overrides:
        if 'vectors' in overrides:
            vec_path = util.match_best_version(overrides['vectors'], None, data_path)
            if vec_path is None: 
                raise IOError(
                    'Could not load data pack %s from %s' % (overrides['vectors'], data_path))

        else:
            vec_path = util.match_best_version('en_glove_cc_300_1m_vectors', None, data_path)
        if vec_path is not None:
            vec_path = vec_path / 'vocab' / 'vec.bin'
            overrides['add_vectors'] = lambda vocab: vocab.load_vectors_from_bin_loc(vec_path)
    path = util.match_best_version(target_name, target_version, data_path)
    cls = get_lang_class(target_name)
    return cls(path=path, **overrides)
