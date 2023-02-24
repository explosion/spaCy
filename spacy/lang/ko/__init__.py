from typing import Iterator, Any, Dict

from .punctuation import TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP
from .lex_attrs import LEX_ATTRS
from ...language import Language, BaseDefaults
from ...tokens import Doc
from ...scorer import Scorer
from ...symbols import POS, X
from ...training import validate_examples
from ...util import DummyTokenizer, registry, load_config_from_str
from ...vocab import Vocab


DEFAULT_CONFIG = """
[nlp]

[nlp.tokenizer]
@tokenizers = "spacy.ko.KoreanTokenizer"
"""


@registry.tokenizers("spacy.ko.KoreanTokenizer")
def create_tokenizer():
    def korean_tokenizer_factory(nlp):
        return KoreanTokenizer(nlp.vocab)

    return korean_tokenizer_factory


class KoreanTokenizer(DummyTokenizer):
    def __init__(self, vocab: Vocab):
        self.vocab = vocab
        self._mecab = try_mecab_import()  # type: ignore[func-returns-value]
        self._mecab_tokenizer = None

    @property
    def mecab_tokenizer(self):
        # This is a property so that initializing a pipeline with blank:ko is
        # possible without actually requiring python-mecab-ko, e.g. to run
        # `spacy init vectors ko` for a pipeline that will have a different
        # tokenizer in the end. The languages need to match for the vectors
        # to be imported and there's no way to pass a custom config to
        # `init vectors`.
        if self._mecab_tokenizer is None:
            self._mecab_tokenizer = self._mecab()
        return self._mecab_tokenizer

    def __reduce__(self):
        return KoreanTokenizer, (self.vocab,)

    def __call__(self, text: str) -> Doc:
        dtokens = self.mecab_tokenizer.parse(text)
        surfaces = [dt.surface for dt in dtokens]

        doc = Doc(self.vocab, words=surfaces, spaces=list(check_spaces(text, surfaces)))

        for token, dtoken in zip(doc, dtokens):
            token.tag_ = dtoken.pos
            first_tag = (
                dtoken.feature.start_pos or dtoken.pos
            )  # stem(어간) or pre-final(선어말 어미)

            if first_tag in TAG_MAP:
                token.pos = TAG_MAP[first_tag][POS]
            else:
                token.pos = X

            token.lemma_ = get_lemma(dtoken)

        return doc

    def score(self, examples):
        validate_examples(examples, "KoreanTokenizer.score")
        return Scorer.score_tokenization(examples)


class KoreanDefaults(BaseDefaults):
    config = load_config_from_str(DEFAULT_CONFIG)
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS
    writing_system = {"direction": "ltr", "has_case": False, "has_letters": False}
    infixes = TOKENIZER_INFIXES


class Korean(Language):
    lang = "ko"
    Defaults = KoreanDefaults


def try_mecab_import():
    try:
        from mecab import MeCab

        return MeCab
    except ImportError:
        raise ImportError(
            'The Korean tokenizer ("spacy.ko.KoreanTokenizer") requires '
            "[python-mecab-ko](https://github.com/jonghwanhyeon/python-mecab-ko). "
            "Install with `pip install python-mecab-ko` or "
            "install spaCy with `pip install spacy[ko]`."
        ) from None


def get_lemma(m):
    expr = m.feature.expression

    if expr is None:
        return m.surface
    else:
        return "+".join([e.split("/")[0] for e in expr.split("+")])


def check_spaces(text, tokens):
    prev_end = -1
    start = 0
    for token in tokens:
        idx = text.find(token, start)
        if prev_end > 0:
            yield prev_end != idx
        prev_end = idx + len(token)
        start = prev_end
    if start > 0:
        yield False


__all__ = ["Korean"]
