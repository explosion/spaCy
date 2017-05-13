# coding: utf8
from __future__ import unicode_literals

from .util import prints
from .cli import download
from . import about


PRON_LEMMA = "-PRON-"


def depr_model_download(lang):
    """Replace en/de download modules within, warn and ownload default models.

    lang (unicode): Language shortcut, 'en' or 'de'.
    """
    prints("The spacy.%s.download command is now deprecated. Please use "
           "python -m spacy download [model name or shortcut] instead. For "
           "more info, see the documentation:" % lang,
           about.__docs_models__,
           "Downloading default '%s' model now..." % lang,
           title="Warning: deprecated command")
    download(lang)


def resolve_load_name(name, **overrides):
    """Resolve model loading if deprecated path kwarg is specified in overrides.

    name (unicode): Name of model to load.
    **overrides: Overrides specified in spacy.load().
    RETURNS: Model name or value of path kwarg.
    """
    if overrides.get('path') not in (None, False, True):
        name = overrides.get('path')
        prints("To load a model from a path, you can now use the first argument. "
               "The model meta is used to load the required Language class.",
               "OLD: spacy.load('en', path='/some/path')", "NEW: spacy.load('/some/path')",
               title="Warning: deprecated argument 'path'")
    return name
