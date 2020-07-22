from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language
from ...tokens import Doc
from ...util import DummyTokenizer, registry


DEFAULT_CONFIG = """
[nlp]
lang = "th"
stop_words = {"@language_data": "spacy.th.stop_words"}
lex_attr_getters = {"@language_data": "spacy.th.lex_attr_getters"}

[nlp.tokenizer]
@tokenizers = "spacy.ThaiTokenizer.v1"
"""


@registry.language_data("spacy.th.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.th.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


@registry.tokenizers("spacy.ThaiTokenizer.v1")
def create_thai_tokenizer():
    def thai_tokenizer_factory(nlp):
        return ThaiTokenizer(nlp)

    return thai_tokenizer_factory


class ThaiTokenizer(DummyTokenizer):
    def __init__(self, nlp: Language) -> None:
        try:
            from pythainlp.tokenize import word_tokenize
        except ImportError:
            raise ImportError(
                "The Thai tokenizer requires the PyThaiNLP library: "
                "https://github.com/PyThaiNLP/pythainlp"
            )
        self.word_tokenize = word_tokenize
        self.vocab = nlp.vocab

    def __call__(self, text: str) -> Doc:
        words = list(self.word_tokenize(text))
        spaces = [False] * len(words)
        return Doc(self.vocab, words=words, spaces=spaces)


class Thai(Language):
    lang = "th"
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Thai"]
