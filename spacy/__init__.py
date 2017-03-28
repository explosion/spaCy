# coding: utf8
from __future__ import unicode_literals

from . import util
from .deprecated import resolve_model_name
from .cli.info import info


from . import en, de, zh, es, it, hu, fr, pt, nl, sv, fi, bn, he, nb


_languages = (en.English, de.German, es.Spanish, pt.Portuguese, fr.French,
             it.Italian, hu.Hungarian, zh.Chinese, nl.Dutch, sv.Swedish,
             fi.Finnish, bn.Bengali, he.Hebrew, nb.Norwegian)


for _lang in _languages:
    util.set_lang_class(_lang.lang, _lang)

from . import en
from . import de
from . import zh
from . import es
from . import it
from . import hu
from . import fr
from . import pt
from . import nl
from . import sv
from . import fi
from . import bn
from . import nb

from .about import *


set_lang_class(en.English.lang, en.English)
set_lang_class(de.German.lang, de.German)
set_lang_class(es.Spanish.lang, es.Spanish)
set_lang_class(pt.Portuguese.lang, pt.Portuguese)
set_lang_class(fr.French.lang, fr.French)
set_lang_class(it.Italian.lang, it.Italian)
set_lang_class(hu.Hungarian.lang, hu.Hungarian)
set_lang_class(zh.Chinese.lang, zh.Chinese)
set_lang_class(nl.Dutch.lang, nl.Dutch)
set_lang_class(sv.Swedish.lang, sv.Swedish)
set_lang_class(fi.Finnish.lang, fi.Finnish)
set_lang_class(bn.Bengali.lang, bn.Bengali)
set_lang_class(nb.Norwegian.lang, nb.Norwegian)
>>>>>>> more norwegian


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


def info(name, markdown):
    info(name, markdown)
