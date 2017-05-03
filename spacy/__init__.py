# coding: utf8
from __future__ import unicode_literals

from . import util
from .deprecated import resolve_model_name
import importlib
from .cli.info import info


_languages_name = set(["en", "de", "es", "pt", "fr",
             "it", "hu", "zh", "nl", "sv",
             "fi", "bn", "he", "nb"])


def load(name, **overrides):
    if overrides.get('path') in (None, False, True):
        data_path = util.get_data_path()
        model_name = resolve_model_name(name)
        model_path = data_path / model_name
        if not model_path.exists():
            lang_name = util.get_lang_class(name).lang
            model_path = None
            util.print_msg(
                "Only loading the '{}' tokenizer.".format(lang_name),
                title="Warning: no model found for '{}'".format(name))
    else:
        model_path = util.ensure_path(overrides['path'])
        data_path = model_path.parent
        model_name = ''
    meta = util.parse_package_meta(data_path, model_name, require=False)
    lang = meta['lang'] if meta and 'lang' in meta else name
    cls = importlib.import_module("."+lang, "spacy")
    overrides['meta'] = meta
    overrides['path'] = model_path
    return cls.EXPORT(**overrides)
