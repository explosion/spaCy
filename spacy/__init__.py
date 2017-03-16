# coding: utf8
from __future__ import unicode_literals, print_function

import json
from pathlib import Path
from .util import set_lang_class, get_lang_class, parse_package_meta

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


def load(name, **overrides):
    data_path = overrides.get('path', util.get_data_path())
    meta = parse_package_meta(data_path, name)
    lang = meta['lang'] if meta and 'lang' in meta else 'en'
    cls = get_lang_class(lang)
    overrides['meta'] = meta
    overrides['path'] = Path(data_path / name)
    return cls(**overrides)
