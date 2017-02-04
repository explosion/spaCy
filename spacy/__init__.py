import pathlib

from .util import set_lang_class, get_lang_class
from .about import __version__

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

try:
    basestring
except NameError:
    basestring = str


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



def load(name, **overrides):
    target_name, target_version = util.split_data_name(name)
    data_path = overrides.get('path', util.get_data_path())
    path = util.match_best_version(target_name, target_version, data_path)
    cls = get_lang_class(target_name)
    overrides['path'] = path
    return cls(**overrides)
