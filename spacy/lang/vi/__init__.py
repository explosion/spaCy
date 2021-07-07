from typing import Any, Dict, Union
from pathlib import Path
import re
import srsly
import string

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language
from ...tokens import Doc
from ...util import DummyTokenizer, registry, load_config_from_str
from ... import util


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
            words = self.pyvi_tokenize(text)
            words, spaces = util.get_words_and_spaces(words, text)
            return Doc(self.vocab, words=words, spaces=spaces)
        else:
            words, spaces = util.get_words_and_spaces(text.split(), text)
            return Doc(self.vocab, words=words, spaces=spaces)

    # The methods pyvi_sylabelize_with_ws and pyvi_tokenize are adapted from
    # pyvi v0.1, MIT License, Copyright (c) 2016 Viet-Trung Tran.
    # See licenses/3rd_party_licenses.txt
    def pyvi_sylabelize_with_ws(self, text):
        """Modified from pyvi to preserve whitespace and skip unicode
        normalization."""
        specials = [r"==>", r"->", r"\.\.\.", r">>"]
        digit = r"\d+([\.,_]\d+)+"
        email = r"([a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z0-9-]+)"
        web = r"\w+://[^\s]+"
        word = r"\w+"
        non_word = r"[^\w\s]"
        abbreviations = [
            r"[A-ZĐ]+\.",
            r"Tp\.",
            r"Mr\.",
            r"Mrs\.",
            r"Ms\.",
            r"Dr\.",
            r"ThS\.",
        ]

        patterns = []
        patterns.extend(abbreviations)
        patterns.extend(specials)
        patterns.extend([web, email])
        patterns.extend([digit, non_word, word])

        patterns = r"(\s+|" + "|".join(patterns) + ")"
        tokens = re.findall(patterns, text, re.UNICODE)

        return [token[0] for token in tokens]

    def pyvi_tokenize(self, text):
        """Modified from pyvi to preserve text and whitespace."""
        if len(text) == 0:
            return []
        elif text.isspace():
            return [text]
        segs = self.pyvi_sylabelize_with_ws(text)
        words = []
        preceding_ws = []
        for i, token in enumerate(segs):
            if not token.isspace():
                words.append(token)
                preceding_ws.append(
                    "" if (i == 0 or not segs[i - 1].isspace()) else segs[i - 1]
                )
        labels = self.ViTokenizer.ViTokenizer.model.predict(
            [self.ViTokenizer.ViTokenizer.sent2features(words, False)]
        )
        token = words[0]
        tokens = []
        for i in range(1, len(labels[0])):
            if (
                labels[0][i] == "I_W"
                and words[i] not in string.punctuation
                and words[i - 1] not in string.punctuation
                and not words[i][0].isdigit()
                and not words[i - 1][0].isdigit()
                and not (words[i][0].istitle() and not words[i - 1][0].istitle())
            ):
                token = token + preceding_ws[i] + words[i]
            else:
                tokens.append(token)
                token = words[i]
        tokens.append(token)
        return tokens

    def _get_config(self) -> Dict[str, Any]:
        return {"use_pyvi": self.use_pyvi}

    def _set_config(self, config: Dict[str, Any] = {}) -> None:
        self.use_pyvi = config.get("use_pyvi", False)

    def to_bytes(self, **kwargs) -> bytes:
        serializers = {"cfg": lambda: srsly.json_dumps(self._get_config())}
        return util.to_bytes(serializers, [])

    def from_bytes(self, data: bytes, **kwargs) -> "VietnameseTokenizer":
        deserializers = {"cfg": lambda b: self._set_config(srsly.json_loads(b))}
        util.from_bytes(data, deserializers, [])
        return self

    def to_disk(self, path: Union[str, Path], **kwargs) -> None:
        path = util.ensure_path(path)
        serializers = {"cfg": lambda p: srsly.write_json(p, self._get_config())}
        return util.to_disk(path, serializers, [])

    def from_disk(self, path: Union[str, Path], **kwargs) -> "VietnameseTokenizer":
        path = util.ensure_path(path)
        serializers = {"cfg": lambda p: self._set_config(srsly.read_json(p))}
        util.from_disk(path, serializers, [])
        return self


class VietnameseDefaults(Language.Defaults):
    config = load_config_from_str(DEFAULT_CONFIG)
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Vietnamese(Language):
    lang = "vi"
    Defaults = VietnameseDefaults


__all__ = ["Vietnamese"]
