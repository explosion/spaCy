import pathlib

from .util import set_lang_class, get_lang_class

from . import en
from . import de
from . import zh


_data_path = pathlib.Path(__file__).parent / 'data'

set_lang_class(en.English.lang, en.English)
set_lang_class(de.German.lang, de.German)
set_lang_class(zh.Chinese.lang, zh.Chinese)


def get_data_path():
    return _data_path


def set_data_path(path):
    global _data_path
    if isinstance(path, basestring):
        path = pathlib.Path(path)
    _data_path = path


def load(name, vocab=None, tokenizer=None, parser=None, tagger=None, entity=None,
         matcher=None, serializer=None, vectors=None, via=None):
    if via is None:
        via = get_data_path()
    cls = get_lang_class(name)
    return cls(
        via,
        vectors=vectors,
        vocab=vocab,
        tokenizer=tokenizer,
        tagger=tagger,
        parser=parser,
        entity=entity,
        matcher=matcher,
        serializer=serializer)
