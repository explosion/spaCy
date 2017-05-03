# coding: utf8
from __future__ import unicode_literals

from . import util
from .deprecated import resolve_model_name
from .cli.info import info
from .glossary import explain

from . import en, de, zh, es, it, hu, fr, pt, nl, sv, fi, bn, he, nb, ja


_languages = (en.English, de.German, es.Spanish, pt.Portuguese, fr.French,
             it.Italian, hu.Hungarian, zh.Chinese, nl.Dutch, sv.Swedish,
             fi.Finnish, bn.Bengali, he.Hebrew, nb.Norwegian, ja.Japanese)


for _lang in _languages:
    util.set_lang_class(_lang.lang, _lang)


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
    cls = util.get_lang_class(lang)
    overrides['meta'] = meta
    overrides['path'] = model_path
    return cls(**overrides)
