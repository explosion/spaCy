# coding: utf8
from __future__ import unicode_literals

from .util import prints
from .cli import download
from . import about


PRON_LEMMA = "-PRON-"


def depr_model_download(lang):
    """
    Replace download modules within en and de with deprecation warning and
    download default language model (using shortcut).
    """
    prints("The spacy.%s.download command is now deprecated. Please use "
           "python -m spacy download [model name or shortcut] instead. For "
           "more info, see the documentation:" % lang,
           about.__docs_models__,
           "Downloading default '%s' model now..." % lang,
           title="Warning: deprecated command")
    download(lang)


def resolve_load_name(name, **overrides):
    if overrides.get('path') not in (None, False, True):
        name = overrides.get('path')
        prints("To load a model from a path, you can now use the first argument. "
               "The model meta is used to load the required Language class.",
               "OLD: spacy.load('en', path='/some/path')", "NEW: spacy.load('/some/path')",
               title="Warning: deprecated argument 'path'")
    return name
