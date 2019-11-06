# coding: utf8
from __future__ import unicode_literals

from ...attrs import LANG
from ...language import Language
from ...tokens import Doc
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP


class YorubaDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "zh"
    use_iranlowo = True
    strip_accents = True
    tokenizer_exceptions = BASE_EXCEPTIONS
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    writing_system = {"direction": "ltr", "has_case": False, "has_letters": False}


class Yoruba(Language):
    lang = "yo"
    Defaults = YorubaDefaults  # override defaults

    def make_doc(self, text):
        if self.Defaults.use_iranlowo:
            try:
                import iranlowo
            except ImportError:
                msg = (
                    "iranlowo is not installed. Either set Yoruba.use_iranlowo = False, "
                    "or install it https://github.com/niger-Volta-LTI/iranlowo"
                )
                raise ImportError(msg)

            text = iranlowo.preprocessing.strip_accents_text(text) if self.Defaults.strip_accents else text
            words = iranlowo.preprocessing.split_corpus_on_symbol(text, symbol=' ')
            words = [word for word in words if word]
            return Doc(self.vocab, words=words, spaces=[False] * len(words))
        else:
            words = []
            spaces = []
            for token in self.tokenizer(text):
                words.extend(list(token.text))
                spaces.extend([False] * len(token.text))
                spaces[-1] = bool(token.whitespace_)
            return Doc(self.vocab, words=words, spaces=spaces)


__all__ = ["Yoruba"]
