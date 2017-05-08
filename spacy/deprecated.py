# coding: utf8
from __future__ import unicode_literals

from . import about
from .util import prints
from .cli import download


PRON_LEMMA = "-PRON-"


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
