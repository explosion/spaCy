# coding: utf8
from __future__ import unicode_literals

from pathlib import Path

from . import about
from . import util
from .util import prints
from .compat import path2str
from .cli import download, link


def fix_glove_vectors_loading(overrides):
    """
    Special-case hack for loading the GloVe vectors, to support deprecated
    <1.0 stuff. Phase this out once the data is fixed.
    """
    if 'data_dir' in overrides and 'path' not in overrides:
        raise ValueError("The argument 'data_dir' has been renamed to 'path'")
    if overrides.get('path') is False:
        return overrides
    if overrides.get('path') in (None, True):
        data_path = util.get_data_path()
    else:
        path = util.ensure_path(overrides['path'])
        data_path = path.parent
    vec_path = None
    if 'add_vectors' not in overrides:
        if 'vectors' in overrides:
            vec_path = match_best_version(overrides['vectors'], None, data_path)
            if vec_path is None:
                return overrides
        else:
            vec_path = match_best_version('en_glove_cc_300_1m_vectors', None, data_path)
        if vec_path is not None:
            vec_path = vec_path / 'vocab' / 'vec.bin'
    if vec_path is not None:
        overrides['add_vectors'] = lambda vocab: vocab.load_vectors_from_bin_loc(vec_path)
    return overrides


def match_best_version(target_name, target_version, path):
    def split_data_name(name):
        return name.split('-', 1) if '-' in name else (name, '')
PRON_LEMMA = "-PRON-"
DET_LEMMA = "-DET-"

    path = util.ensure_path(path)
    if path is None or not path.exists():
        return None
    matches = []
    for data_name in path.iterdir():
        name, version = split_data_name(data_name.parts[-1])
        if name == target_name:
            matches.append((tuple(float(v) for v in version.split('.')), data_name))
    if matches:
        return Path(max(matches)[1])
    else:
        return None


def resolve_model_name(name):
    """
    If spaCy is loaded with 'de', check if symlink already exists. If
    not, user may have upgraded from older version and have old models installed.
    Check if old model directory exists and if so, return that instead and create
    shortcut link. If English model is found and no shortcut exists, raise error
    and tell user to install new model.
    """
    if name == 'en' or name == 'de':
        versions = ['1.0.0', '1.1.0']
        data_path = util.get_data_path()
        model_path = data_path / name
        v_model_paths = [data_path / '%s-%s' % (name, v) for v in versions]

        if not model_path.exists(): # no shortcut found
            for v_path in v_model_paths:
                if v_path.exists(): # versioned model directory found
                    if name == 'de':
                        link(v_path, name)
                        return name
                    else:
                        raise ValueError(
                            "Found English model at %s. This model is not "
                            "compatible with the current version. See "
                            "https://spacy.io/docs/usage/models to download the "
                            "new model." % path2str(v_path))
    return name


def depr_model_download(lang):
    """
    Replace download modules within en and de with deprecation warning and
    download default language model (using shortcut).
    """
    prints("The spacy.%s.download command is now deprecated. Please use "
           "python -m spacy download [model name or shortcut] instead. For "
           "more info, see the docs: %s." % (lang, about.__docs__),
           "Downloading default '%s' model now..." % lang,
           title="Warning: deprecated command")
    download(lang)
