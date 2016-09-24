import pathlib

from .util import set_lang_class, get_lang_class

from . import en
from . import de
from . import zh


set_lang_class(en.English.lang, en.English)
set_lang_class(de.German.lang, de.German)
set_lang_class(zh.Chinese.lang, zh.Chinese)


def load(name, vocab=True, tokenizer=True, parser=True, tagger=True, entity=True,
         matcher=True, serializer=True, vectors=True, via=None):
    if via is None:
        via = util.get_data_path()

    target_name, target_version = util.split_data_name(name)
    path = util.match_best_version(target_name, target_version, via)

    if isinstance(vectors, basestring):
        vectors_name, vectors_version = util.split_data_name(vectors)
        vectors = util.match_best_version(vectors_name, vectors_version, via)
    
    cls = get_lang_class(target_name)
    return cls(
        path,
        vectors=vectors,
        vocab=vocab,
        tokenizer=tokenizer,
        tagger=tagger,
        parser=parser,
        entity=entity,
        matcher=matcher,
        serializer=serializer)
