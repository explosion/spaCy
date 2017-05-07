# coding: utf8
from __future__ import unicode_literals

from . import util
from .util import prints
from .deprecated import resolve_model_name
import importlib
from .cli.info import info
from .glossary import explain


_languages_name = set(["en", "de", "es", "pt", "fr",
             "it", "hu", "zh", "nl", "sv",
             "fi", "bn", "he", "nb", "ja"])


def load(name, **overrides):
    if overrides.get('path') in (None, False, True):
        data_path = util.get_data_path()
        model_name = resolve_model_name(name)
        model_path = data_path / model_name
        if not model_path.exists():
            lang_name = util.get_lang_class(name).lang
            model_path = None
            prints("Only loading the '%s' tokenizer." % lang_name,
                   title="Warning: no model found for '%s'" % name)
    else:
        model_path = util.ensure_path(overrides['path'])
        data_path = model_path.parent
        model_name = ''
    meta = util.parse_package_meta(data_path, model_name, require=False)
    lang = meta['lang'] if meta and 'lang' in meta else name
    module = importlib.import_module("."+lang, "spacy")
    cls = module.EXPORT
    overrides['meta'] = meta
    overrides['path'] = model_path
    return cls(**overrides)
