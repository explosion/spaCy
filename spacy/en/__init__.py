# encoding: utf8
from __future__ import unicode_literals, print_function

from os import path

from ..util import match_best_version
from ..util import get_data_path
from ..language import Language
from ..lemmatizer import Lemmatizer
from ..vocab import Vocab
from ..tokenizer import Tokenizer
from ..attrs import LANG

from .language_data import *


class English(Language):
    lang = 'en'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'en'

        tokenizer_exceptions = TOKENIZER_EXCEPTIONS
        tag_map = TAG_MAP
        stop_words = STOP_WORDS
        lemma_rules = LEMMA_RULES


    def __init__(self, **overrides):
        # Make a special-case hack for loading the GloVe vectors, to support
        # deprecated <1.0 stuff. Phase this out once the data is fixed.
        overrides = _fix_deprecated_glove_vectors_loading(overrides)
        Language.__init__(self, **overrides)


def _fix_deprecated_glove_vectors_loading(overrides):
    if 'data_dir' in overrides and 'path' not in overrides:
        raise ValueError("The argument 'data_dir' has been renamed to 'path'")
    if overrides.get('path') is False:
        return overrides
    if overrides.get('path') in (None, True):
        data_path = get_data_path()
    else:
        path = overrides['path']
        data_path = path.parent
    vec_path = None
    if 'add_vectors' not in overrides:
        if 'vectors' in overrides:
            vec_path = match_best_version(overrides['vectors'], None, data_path)
            if vec_path is None:
                raise IOError(
                    'Could not load data pack %s from %s' % (overrides['vectors'], data_path))
        else:
            vec_path = match_best_version('en_glove_cc_300_1m_vectors', None, data_path)
        if vec_path is not None:
            vec_path = vec_path / 'vocab' / 'vec.bin'
    if vec_path is not None:
        overrides['add_vectors'] = lambda vocab: vocab.load_vectors_from_bin_loc(vec_path)
    return overrides
