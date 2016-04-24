from .util import set_lang_class, get_lang_class, get_package, get_package_by_name

from . import en
from . import de
from . import zh


set_lang_class(en.English.lang, en.English)
set_lang_class(de.German.lang, de.German)
set_lang_class(zh.Chinese.lang, zh.Chinese)


def load(name, vocab=None, tokenizer=None, parser=None, tagger=None, entity=None,
         matcher=None, serializer=None, vectors=None, via=None):
    package = get_package_by_name(name, via=via)
    vectors_package = get_package_by_name(vectors, via=via)
    cls = get_lang_class(name)
    return cls(
        package=package,
        vectors_package=vectors_package,
        vocab=vocab,
        tokenizer=tokenizer,
        tagger=tagger,
        parser=parser,
        entity=entity,
        matcher=matcher,
        serializer=serializer)
