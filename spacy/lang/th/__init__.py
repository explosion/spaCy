# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS

from ...tokens import Doc
from ...language import Language
from ...attrs import LANG


class ThaiDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "th"
    tokenizer_exceptions = dict(TOKENIZER_EXCEPTIONS)
    tag_map = TAG_MAP
    stop_words = STOP_WORDS


class Thai(Language):
    lang = "th"
    Defaults = ThaiDefaults

    def make_doc(self, text):
        try:
            from pythainlp.tokenize import word_tokenize
        except ImportError:
            raise ImportError(
                "The Thai tokenizer requires the PyThaiNLP library: "
                "https://github.com/PyThaiNLP/pythainlp"
            )
        words = [x for x in list(word_tokenize(text, "newmm"))]
        return Doc(self.vocab, words=words, spaces=[False] * len(words))


__all__ = ["Thai"]
