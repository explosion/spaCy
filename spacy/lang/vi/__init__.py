from typing import Set, Dict, Callable, Any
from thinc.api import Config

from ...language import Language
from ...tokens import Doc
from .stop_words import STOP_WORDS
from ...util import DummyTokenizer, registry
from .lex_attrs import LEX_ATTRS


DEFAULT_CONFIG = """
[nlp]
lang = "vi"
stop_words = {"@language_data": "spacy.vi.stop_words"}
lex_attr_getters = {"@language_data": "spacy.vi.lex_attr_getters"}

[nlp.tokenizer]
@tokenizers = "spacy.VietnameseTokenizer.v1"
use_pyvi = true
"""


@registry.language_data("spacy.vi.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.vi.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


@registry.tokenizers("spacy.VietnameseTokenizer.v1")
def create_vietnamese_tokenizer(use_pyvi: bool = True,):
    def vietnamese_tokenizer_factory(nlp):
        return VietnameseTokenizer(nlp, use_pyvi=use_pyvi)

    return vietnamese_tokenizer_factory


class VietnameseTokenizer(DummyTokenizer):
    def __init__(self, nlp: Language, use_pyvi: bool = False):
        self.vocab = nlp.vocab
        self.use_pyvi = use_pyvi
        if self.use_pyvi:
            try:
                from pyvi import ViTokenizer

                self.ViTokenizer = ViTokenizer
            except ImportError:
                msg = (
                    "Pyvi not installed. Either set use_pyvi = False, "
                    "or install it https://pypi.python.org/pypi/pyvi"
                )
                raise ImportError(msg)

    def __call__(self, text: str) -> Doc:
        if self.use_pyvi:
            words, spaces = self.ViTokenizer.spacy_tokenize(text)
            return Doc(self.vocab, words=words, spaces=spaces)
        else:
            words = []
            spaces = []
            for token in self.tokenizer(text):
                words.extend(list(token.text))
                spaces.extend([False] * len(token.text))
                spaces[-1] = bool(token.whitespace_)
            return Doc(self.vocab, words=words, spaces=spaces)


class Vietnamese(Language):
    lang = "vi"
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Vietnamese"]
