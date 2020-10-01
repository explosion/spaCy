from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language
from ...tokens import Doc
from ...util import DummyTokenizer, registry, load_config_from_str


DEFAULT_CONFIG = """
[nlp]

[nlp.tokenizer]
@tokenizers = "spacy.vi.VietnameseTokenizer"
use_pyvi = true
"""


@registry.tokenizers("spacy.vi.VietnameseTokenizer")
def create_vietnamese_tokenizer(use_pyvi: bool = True):
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
                raise ImportError(msg) from None

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


class VietnameseDefaults(Language.Defaults):
    config = load_config_from_str(DEFAULT_CONFIG)
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Vietnamese(Language):
    lang = "vi"
    Defaults = VietnameseDefaults


__all__ = ["Vietnamese"]
